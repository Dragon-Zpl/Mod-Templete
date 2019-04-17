from abc import ABCMeta,abstractmethod

class Parser(metaclass=ABCMeta):

    """
    信息解析
    """

    @abstractmethod
    def _parse(self, html:str) ->dict:
        print('__parse come in')
        return {}

    def parse(self, html:str) -> dict:
        """暴露的接口"""
        print('parse comein ')
        return self._parse(html)




#
# class Parser(metaclass=ABCMeta):
#
#     """
#     信息解析
#     """
#
#     # @abstractmethod
#     def _parse(self, html:str, xpath_dict:dict) ->dict:
#         return_dict = {}
#         content = etree.HTML(html)
#         for k,v in xpath_dict.items():
#             if content.xpath(v):
#                 return_dict[k] = content.xpath(v)
#             else:
#                 return_dict[k] = ""
#         return return_dict
#
#     def parse(self, html:str, xpath_dict:dict) -> dict:
#         """暴露的接口"""
#         return self._parse(html, xpath_dict)



