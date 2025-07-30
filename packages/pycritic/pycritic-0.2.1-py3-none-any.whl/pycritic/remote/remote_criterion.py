import typing as t

import requests

from ..base import Criterion, Estimand, Estimation



class RemoteHTTPCriterion(Criterion[Estimation]):
    """The network-based criterion
    
    Than criterion does an HTTP-request to a server in order to get an
    estimation
    """


    def __init__(
        self,
        url: str,
        responseHander: t.Callable[[requests.Response], Estimation]
    ) -> None:
        """
        
        :param url: URL of a server
        :type url: str

        :param responseHandler: Response-processing function
        :type responseHander: typing.Callable[[requests.Response], Estimation]
        """
        self.__url = url
        self.__respHandler = responseHander


    def __call__(self, estimand: Estimand) -> Estimation:
        """
        
        :param estimand: An estimand
        :type estimand: Estimand

        :return: An estimation
        :rtype: Estimation
        """
        resp = requests.post(self.__url, json=estimand)
        return self.__respHandler(resp)
