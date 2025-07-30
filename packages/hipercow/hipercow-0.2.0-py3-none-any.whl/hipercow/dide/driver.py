from pathlib import Path

from taskwait import Task, taskwait

from hipercow import ui
from hipercow.dide.auth import fetch_credentials
from hipercow.dide.batch import write_batch_provision, write_batch_task_run
from hipercow.dide.configuration import DideConfiguration, dide_configuration
from hipercow.dide.mounts import detect_mounts
from hipercow.dide.web import DideWebClient
from hipercow.driver import HipercowDriver, hipercow_driver
from hipercow.resources import ClusterResources, Queues, TaskResources
from hipercow.root import Root


@hipercow_driver
class DideWindowsDriver(HipercowDriver):
    name = "dide-windows"
    config: DideConfiguration

    def __init__(self, config: DideConfiguration):
        self.config = config

    @staticmethod
    def configure(root: Root, **kwargs) -> DideConfiguration:
        mounts = detect_mounts()
        return dide_configuration(root, mounts=mounts, **kwargs)

    @staticmethod
    def parse_configuration(data: str) -> DideConfiguration:
        return DideConfiguration.model_validate_json(data)

    def configuration(self) -> DideConfiguration:
        return self.config

    def show_configuration(self) -> None:
        path_map = self.config.path_map
        ui.li("[bold]Path mapping[/bold]")
        ui.li(f"drive '{path_map.remote}'", indent=2, symbol="-")
        ui.li(
            f"share '\\\\{path_map.mount.host}\\{path_map.mount.remote}'",
            indent=2,
            symbol="-",
        )
        ui.li(f"[bold]Python version[/bold]: {self.config.python_version}")

    def submit(
        self, task_id: str, resources: TaskResources | None, root: Root
    ) -> None:
        cl = _web_client()
        unc = write_batch_task_run(task_id, self.config, root)
        if not resources:
            resources = self.resources().validate_resources(TaskResources())
        dide_id = cl.submit(unc, task_id, resources=resources)
        with self._path_dide_id(task_id, root).open("w") as f:
            f.write(dide_id)

    def provision(self, name: str, id: str, root: Root) -> None:
        _dide_provision(name, id, self.config, root)

    def resources(self) -> ClusterResources:
        # We should get this from the cluster itself but with caching
        # not yet configured this seems unwise as we'll hit the
        # cluster an additional time for every job submission rather
        # than just once a session.
        queues = Queues(
            {"AllNodes", "BuildQueue", "Testing"},
            default="AllNodes",
            test="Testing",
            build="BuildQueue",
        )
        return ClusterResources(queues=queues, max_cores=32, max_memory=512)

    def task_log(
        self, task_id: str, *, outer: bool = False, root: Root
    ) -> str | None:
        if outer:
            with self._path_dide_id(task_id, root).open() as f:
                dide_id = f.read().strip()
            cl = _web_client()
            return cl.log(dide_id.strip())
        return super().task_log(task_id, outer=False, root=root)

    def _path_dide_id(self, task_id: str, root: Root) -> Path:
        return root.path_task(task_id) / "dide_id"


class ProvisionWaitWrapper(Task):
    def __init__(
        self,
        root: Root,
        name: str,
        provision_id: str,
        client: DideWebClient,
        dide_id: str,
    ):
        self.root = root
        self.name = name
        self.provision_id = provision_id
        self.client = client
        self.dide_id = dide_id
        self.status_waiting = {"created", "submitted"}
        self.status_running = {"running"}

    def status(self) -> str:
        return str(self.client.status_job(self.dide_id))

    def log(self) -> list[str] | None:
        path = self.root.path_provision_log(self.name, self.provision_id)
        if not path.exists():
            return None
        with path.open() as f:
            return f.read().splitlines()

    def has_log(self) -> bool:
        return True


def _web_client() -> DideWebClient:
    credentials = fetch_credentials()
    cl = DideWebClient(credentials)
    cl.login()
    return cl


def _dide_provision(name: str, id: str, config: DideConfiguration, root: Root):
    cl = _web_client()
    unc = write_batch_provision(name, id, config, root)
    resources = TaskResources(queue="BuildQueue")
    dide_id = cl.submit(unc, f"{name}/{id}", resources=resources)
    task = ProvisionWaitWrapper(root, name, id, cl, dide_id)
    res = taskwait(task)
    dt = round(res.end - res.start, 2)
    if res.status == "failure":
        path_log = root.path_provision_log(name, id, relative=True)
        ui.alert_danger(f"Provisioning failed after {dt}s!")
        ui.blank_line()
        ui.text("Logs, if produced, may be visible above")
        ui.text("A copy of all logs is available at:")
        ui.text(f"    {path_log}")
        ui.blank_line()
        dide_log = cl.log(dide_id)
        ui.logs("Logs from the cluster", dide_log)
        msg = "Provisioning failed"
        raise Exception(msg)
    else:
        ui.alert_success(f"Provisioning completed in {dt}s")
