from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time
from contextlib import asynccontextmanager
from .cli import receive_task, complete_task, list_all_tasks, list_all_tasks_new, receive_task_new, complete_task_new
from .workday_facade import WorkdayFacade
from pydantic import BaseModel
from typing import List


workday_facade = WorkdayFacade()



async def perform_startup_tasks():
    """ 1 """
    print("Performing startup tasks...")
    scheduler.start()
    print("APScheduler 启动")
    # Your existing startup logic here

async def perform_shutdown_tasks():
    """ 1 """
    print("Performing shutdown tasks...")
    scheduler.shutdown()
    print("APScheduler 关闭")
    # Your existing shutdown logic here

class TaskRequest(BaseModel):
    """ 1 """
    task: str

# old
class TaskListRequest(BaseModel):
    tasks: List

class TaskListJSONRequest(BaseModel):
    tasks: List[dict]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """_summary_

    Args:
        app (FastAPI): _description_
    """
    await perform_startup_tasks()
    yield
    await perform_shutdown_tasks()


app = FastAPI(lifespan=lifespan)



def task_daily_midnight():
    """
    每天凌晨 0:00 执行的任务
    """
    print(f"任务：每天凌晨 0:00 执行。当前时间：{time.ctime()}")
    workday_facade.clear()

def task_weekday_3am():
    """
    工作日 3:00 执行的任务
    """
    print(f"任务：工作日 3:00 执行。当前时间：{time.ctime()}")
    workday_facade._morning_tasks()

def task_weekday_850am():
    """
    工作日 8:50 执行的任务
    """
    print(f"任务：工作日 9:30 执行。当前时间：{time.ctime()}")
    workday_facade._start_work_tasks()


def task_weekday_6pm():
    """
    工作日 18:00 执行的任务
    """
    print(f"任务：工作日 18:00 执行。当前时间：{time.ctime()}")
    workday_facade._finish_work_tasks()

def task_weekday_7pm():
    """
    工作日 19:00 执行的任务
    """
    print(f"任务：工作日 19:00 执行。当前时间：{time.ctime()}")
    workday_facade._evening_tasks()

def task_weekend_8am():
    """
    休息日 5:00 执行的任务
    """
    print(f"任务：休息日 5:00 执行。当前时间：{time.ctime()}")
    workday_facade._rest()

scheduler = BackgroundScheduler()
# TODO 修改自动日程执行
# 每天的凌晨 0:00
scheduler.add_job(task_daily_midnight, CronTrigger(hour=0, minute=0))

# 每日 的 3:00
scheduler.add_job(task_weekday_3am, CronTrigger(hour=3, minute=0, 
                                                # day_of_week='mon-fri'
                                                ))

# 工作日 (周一到周五) 的 8:50
scheduler.add_job(task_weekday_850am, CronTrigger(hour=8, minute=50, day_of_week='mon-fri'))

# 工作日 (周一到周五) 的 18:00
scheduler.add_job(task_weekday_6pm, CronTrigger(hour=18, minute=0, day_of_week='mon-fri'))

# 每日 的 19:00
scheduler.add_job(task_weekday_7pm, CronTrigger(hour=19, minute=0, 
                                                # day_of_week='mon-fri'
                                                ))

# 休息日 (周六和周日) 的 8:00
scheduler.add_job(task_weekend_8am, CronTrigger(hour=8, minute=0, day_of_week='sat,sun'))


def adapter(text):
    import re
    # 使用正则表达式匹配 "当前任务：" 后面的内容，直到第一个空格或括号
    regex = r"当前任务：(.*?)(?:\s|\()"
    regex = r"当前任务：(.*?)(?:\n|$)"
    match = re.search(regex, text)

    if match:
        task_name = match.group(1)
        return task_name
    else:
        print(f'提取失败: -> {text}')
        return text

@app.get("/receive")
async def receive():
    result = receive_task()
    return {"message": adapter(result)}

@app.get("/receive_new/{id}")
async def receive_new(id:str):
    result = receive_task_new(id)
    return {"message": adapter(result)}

@app.get("/complete")
async def complete():
    result = complete_task()
    return {"message": adapter(result)}

@app.get("/complete_new/{id}")
async def complete_new(id:str):
    result = complete_task_new(id)
    return {"message": adapter(result)}

@app.post("/update_tasks")
async def update_tasks(task_request:TaskListRequest):
    print(task_request.tasks,'tasks')
    result = workday_facade.add_person_tasks(task_request.tasks)
    return {"message": result}

@app.post("/update_tasks_new")
async def update_tasks_new(task_request:TaskListJSONRequest):
    print(task_request.tasks,'tasks')
    # [{'content': 'Complete project report'}, {'content': 'Attend team meeting'}, {'content': 'Review code'}] tasks
    result = workday_facade.add_person_tasks_new(task_request.tasks)

    return {"message": result}



@app.get("/list_tasks")
async def list_tasks():
    result = list_all_tasks()
    return {"message": result}


@app.get("/list_tasks_new/{id}")
async def list_tasks_new(id):
    result = list_all_tasks_new(id)
    return {"message": result}


@app.get("/morning")
async def morning():
    result = workday_facade._morning_tasks()
    print(result)
    return {"message": "FastAPI and APScheduler configured."}

@app.get("/morning_new/{id}")
async def morning_new(id:str):
    print(id,'id')
    result = workday_facade._morning_tasks_new(id)
    print(result)
    return {"message": "FastAPI and APScheduler configured."}


@app.get("/clear")
async def clear():
    workday_facade.clear()
    return {"message": "FastAPI and APScheduler configured."}

@app.get("/clear_new")
async def clear_new():
    workday_facade.clear_new()
    return {"message": "FastAPI and APScheduler configured."}

if __name__ == "__main__":
    import argparse
    import uvicorn
    from .log import Log
    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        nargs='?',
        default=8020,
        help='Specify alternate port [default: 8000]'
    )

    # 创建一个互斥组用于环境选择
    group = parser.add_mutually_exclusive_group()

    # 添加 --dev 选项
    group.add_argument(
        '--dev',
        action='store_true', # 当存在 --dev 时，该值为 True
        help='Run in development mode (default).'
    )

    # 添加 --prod 选项
    group.add_argument(
        '--prod',
        action='store_true', # 当存在 --prod 时，该值为 True
        help='Run in production mode.'
    )

    args = parser.parse_args()


    if args.prod:
        env = "prod"
    else:
        # 如果 --prod 不存在，默认就是 dev
        env = "dev"


    reload = False # 默认不热重载

    port = args.port
    if env == "dev":
        port += 100
        Log.reset_level('debug',env = env)
        reload = True
        app_import_string = "src.reallife.server:app" # <--- 关键修改：传递导入字符串
    elif env == "prod":
        Log.reset_level('info',env = env)# ['debug', 'info', 'warning', 'error', 'critical']
        reload = False
        app_import_string = app
    else:
        reload = False
        app_import_string = app

    uvicorn.run(
        # app, # 要加载的应用，格式是 "module_name:variable_name"
        app_import_string,
        host="0.0.0.0",
        port=port,
        reload=reload  # 启用热重载
    )
