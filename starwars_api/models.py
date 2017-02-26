from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for k,v in json_data.items():
            setattr(self,k,v)

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        f = 'get_{0}'.format(cls.RESOURCE_NAME)
        return cls(getattr(api_client,f)(resource_id))

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        f = "{0}QuerySet".format(cls.__name__)
        return eval(f)()


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):
    def __init__(self):
        self.pageNum = 0
        self.totalCnt=0
        self.objects = []
        self.counter = 0
        self.get_next_page()

    def __iter__(self):
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        while True:
            if self.totalCnt == self.counter:
                raise StopIteration
            if self.totalCnt > len(self.objects):
                self.get_next_page()
            if self.counter <= len(self.objects):
                elem = self.objects[self.counter]
                self.counter+=1
            return elem
            
                
    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return self.totalCnt
    
    def get_next_page(self):
        """ 
        Send a new request to API
        Create objects and append to self.objects
        """
        self.pageNum+=1
        get_func = "get_{0}".format(self.RESOURCE_NAME) #i.e get_people
        json_data = getattr(api_client,get_func)(page=self.pageNum)
        self.totalCnt = json_data['count']
        obj = eval(self.RESOURCE_NAME.title())
        for j in json_data['results']:
            o = obj(j)
            self.objects.append(o)
        


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
