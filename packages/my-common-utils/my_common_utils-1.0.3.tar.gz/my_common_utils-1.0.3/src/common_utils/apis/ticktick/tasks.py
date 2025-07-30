import requests
from pydantic import BaseModel, ConfigDict

from common_utils.apis.ticktick.cookies_login import get_authenticated_ticktick_headers
from common_utils.logger import create_logger


class TickTickTask(BaseModel):
    id: str
    project_id: str
    title: str
    status: int
    priority: int
    deleted: int
    created_time: str
    creator: int
    items: list
    project_name: str | None = None
    column_id: str | None = None
    is_all_day: bool | None = None
    start_date: str | None = None
    due_date: str | None = None
    content: str | None = None

    @staticmethod
    def to_camel(field_name: str) -> str:
        """
        Convert a snake_case field name into camelCase.
        E.g. 'checkin_stamp' -> 'checkinStamp'
        """
        parts = field_name.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow"
    )


class TickTickProject(BaseModel):
    id: str
    name: str
    is_owner: bool
    in_all: bool
    group_id: str | None
    muted: bool


    @staticmethod
    def to_camel(field_name: str) -> str:
        """
        Convert a snake_case field name into camelCase.
        E.g. 'checkin_stamp' -> 'checkinStamp'
        """
        parts = field_name.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow"
    )



class TicktickTaskHandler:
    log = create_logger("TickTick Task Handler")
    url_get_tasks = 'https://api.ticktick.com/api/v2/batch/check/0'
    url_get_projects = 'https://api.ticktick.com/api/v2/projects'

    def __init__(
            self,
            return_pydantic: bool = True,
            always_raise_exceptions: bool = False,
            cookies_path: str | None = None,
            username_env: str = 'TICKTICK_EMAIL',
            password_env: str = 'TICKTICK_PASSWORD',
            headless: bool = True,
            undetected: bool = False,
            download_driver: bool = False,
    ):
        self.headers = get_authenticated_ticktick_headers(
            cookies_path=cookies_path,
            username_env=username_env,
            password_env=password_env,
            headless=headless,
            undetected=undetected,
            download_driver=download_driver,
        )
        self.raise_exceptions = always_raise_exceptions
        self.return_pydantic = return_pydantic
        self.projects = None

    def get_all_tasks(self) -> list[TickTickTask] | list[dict] | None:
        """
        Get all TickTick tasks

        Returns:
            List of TickTickTask pydantic BaseModel objects, or dicts
        """
        response = requests.get(url=self.url_get_tasks, headers=self.headers).json()
        tasks_data = response.get('syncTaskBean', {}).get('update', None)
        if tasks_data is None:
            self.log_or_raise_error('Getting Tasks failed')
            return None

        tasks = [TickTickTask(**task_data) for task_data in tasks_data]
        tasks = self.add_project_titles_to_tasks(tasks)

        return tasks

    def get_all_projects(self) -> dict[str, TickTickProject]:
        response = requests.get(url=self.url_get_projects, headers=self.headers).json()
        if response is None:
            self.log_or_raise_error('Getting Projects failed')
            return None

        projects = [TickTickProject(**project_data) for project_data in response]
        projects_map = {project.id: project for project in projects}
        self.projects = projects_map

        return projects_map

    def add_project_titles_to_tasks(self, tasks: list[TickTickTask]) -> list[TickTickTask]:
        if not self.projects:
            return tasks

        for task in tasks:
            try:
                if 'inbox' in task.project_id:
                    task.project_name = 'INBOX'
                else:
                    task.project_name = self.projects[task.project_id].name
            except:
                self.log.warning(f'Project of task {task.title} not found')

        return tasks

    def log_or_raise_error(self, error_msg: str) -> None:
        if self.raise_exceptions:
            raise ValueError(error_msg)
        else:
            self.log.error(error_msg)




if __name__ == '__main__':
    TicktickTaskHandler().get_all_tasks()