
import pytest

from kanbanz import Kanban,Pool

@pytest.fixture
def kanban_create():
    kanban_path = "/Users/zhaoxuefeng/GitHub/obsidian/工作/事件看板/实验看板.md"
    cm = Kanban(kanban_path)
    cm.pull()

    yield cm
    cm.push()


def test_insert(kanban_create):
    print(kanban_create.insert('知识',Pool.预备池))

def test_get_tasks_in(kanban_create):
    print(kanban_create.get_tasks_in(Pool.预备池))

def test_pop(kanban_create):
    print(kanban_create.pop('等待反馈',Pool.预备池))

def test_get_task_by_word(kanban_create):
    print(kanban_create.get_task_by_word('知识',Pool.预备池))

from kanbanz.manager import KanBanManager

kanban_path = "/Users/zhaoxuefeng/GitHub/obsidian/实验室/ceshi.md"


import importlib.resources

import yaml

def load_config():
    with open('config.yaml','r') as f:
        return yaml.safe_load(f)

x = load_config().get('WORK_CANVAS_PATH')

kb = KanBanManager(kanban_path=kanban_path,pathlib=x)

kb.sync_ready()

kb.sync_order()

kb.sync_run()

kb.sync_run2order()

kb.sync_run2over(task = '',
                canvas_path:str)

