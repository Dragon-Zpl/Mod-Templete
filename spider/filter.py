from abc import ABCMeta,abstractmethod

class Filter(metaclass=ABCMeta):
    @abstractmethod
    def _filter(self, *args, **kwargs):
        pass

    def filter(self, *args, **kwargs):
        """
        过滤app
        :return:
        """
        return self.filter(*args, **kwargs)