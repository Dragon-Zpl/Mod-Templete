from abc import ABCMeta,abstractmethod

class Filter(metaclass=ABCMeta):
    @abstractmethod
    def _filter(self, *args, **kwargs)->bool:

        return True

    def filter(self, *args, **kwargs):
        print('fiter jiekou')
        """
        过滤app
        :return:
        """
        return self.filter(*args, **kwargs)