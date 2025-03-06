config = dict(handlers=[
    dict(
        sink='logs/logging.txt',
        format="<level><green>{time:YYYY-MM-DD HH:mm:ss.SS}</green> | {level:<5} |"
               "|{thread.name:<22}|{function:>16}:{line:<3}|"
               "<cyan>{message:<}</cyan></level>",
        level="DEBUG",
        rotation='1 month',
        enqueue=True,

    ),

])
