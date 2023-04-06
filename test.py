
import flytekit
from flytekit import task, workflow
# from flytekit.deck.deck import measure_execution_time

@task(disable_deck=False)
def t1():
    # import time
    # with measure_execution_time("download data from s3"):
    #     time.sleep(1)
    # with measure_execution_time("train"):
    #     time.sleep(2)
    print("!!! I am in user code !!!")
    print(flytekit.current_context().default_deck.name)
    print(flytekit.current_context().time_line_deck.name)
   
    
@workflow
def wf():
    t1()

if __name__ == "__main__":
    wf()   