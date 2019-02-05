

def p_decorate(func):
    def func_wrapper(*args, **kwargs):
        return "<p> {0} </p>".format(func(*args, **kwargs))
    
    return func_wrapper


class Person(object):
    def __init__(self):
        self.name = "John"
        self.family = "Doe"

    @p_decorate
    def get_fullname(self):
        return self.name + " " + self.family


my_person = Person()
print(my_person.get_fullname())


@p_decorate
def my_message(name):
    return "Hello " + name


print(my_message("Zari"))


def tags(tag_name):
    def tags_decorator(func):
        def func_wrapper(name):
            return "<{0}> {1} </{0}>".format(tag_name, func(name))

        return func_wrapper

    return tags_decorator


@tags("p")
def greet(name):
    return "Hello " + name


print(greet("Zari"))



