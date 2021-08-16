import os
import logging
import logging.handlers


class LogHandler(logging.FileHandler):
    pass
    # def doRollover(self):
    #     if self.stream:
    #         self.stream.close()
    #         self.stream = None
    #     if self.backupCount > 0:
    #         filename, file_extension = os.path.splitext(self.baseFilename)
    #         for i in range(self.backupCount - 1, 0, -1):
    #             sfn = self.rotation_filename(f'{filename}_{i}{file_extension}')
    #             dfn = self.rotation_filename(f'{filename}_{i+1}{file_extension}')
    #             if os.path.exists(sfn):
    #                 if os.path.exists(dfn):
    #                     os.remove(dfn)
    #                 os.rename(sfn, dfn)
    #         dfn = self.rotation_filename(f'{filename}_1{file_extension}')
    #         if os.path.exists(dfn):
    #             os.remove(dfn)
    #         self.rotate(self.baseFilename, dfn)
    #     if not self.delay:
    #         self.stream = self._open()


def get_logger(f_handler):
    logger = logging.getLogger("Maze", )
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(name)s] [%(asctime)s] [%(levelname)s] - %(message)s')
    f_handler.setFormatter(formatter)
    logger.addHandler(f_handler)
    return logger


def get_handler(filename):
    return LogHandler(filename, mode='w',
                      # backupCount=5, maxBytes=10
                      )
