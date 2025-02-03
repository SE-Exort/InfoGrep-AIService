import concurrent.futures
from Parsers.Parser import Parser


class ParserThreadPool:
    def __init__(self, max_workers):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers);
        self.taskstatus=dict()

    def create_taskkey(self, chatroom_uuid, file_uuid):
        return chatroom_uuid + file_uuid;

    def submit_task(self, task: Parser):
        taskkey = self.create_taskkey(task.getChatRoomUUID(), task.getFileUUID());

        self.executor.submit(task.startParsing);
        self.taskstatus.update({taskkey: task})


    def cancel_task(self, taskkey):
        if taskkey in self.taskstatus:
            self.taskstatus.get(taskkey).cancelParsing();
        return

    def get_task_status(self, taskkey):
        if taskkey in self.taskstatus:
            self.taskstatus.get(taskkey).getParsingStatus();
        else:
            return 403

