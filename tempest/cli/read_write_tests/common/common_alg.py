import time
from tempest import exceptions

def wait_and_throw_on_timeout(
    condition,
    delay,
    timeout,
    message="Timeout occurred waiting for condition"
):
    """Performs busy-wait (with delay) until given condition becomes true.
    Loop is limited by timeout.

    @param condition: function to be used as a loop condition.
    It's result has to be convertible to bool.
    @param delay: interval after which condition should be checked
    @param timeout: Number of seconds after which error will be thrown

    @todo: The function should be moved to library of helper functions
    """
    end_time = int(time.time()) + timeout
    while not condition():
        time_left = end_time - int(time.time())
        if delay > time_left:
            raise exceptions.TimeoutException(message)
        time.sleep(delay)
