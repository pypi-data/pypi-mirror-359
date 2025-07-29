import abc


class Serializable(abc.ABC):
    """
    An abstract base class for objects that can be serialized.

    This interface defines a contract for classes that need to convert their
    instances to a serializable format (like dict, list, or primitive types)
    that can be easily converted to JSON, YAML, or other formats.

    Example:
        class User(Serializable):
            def __init__(self, name, email):
                self.name = name
                self.email = email

            def serialize(self):
                return {
                    'name': self.name,
                    'email': self.email
                }
    """
    @abc.abstractmethod
    def serialize(self):
        """
        Convert the object to a serializable format.

        This method should be implemented by subclasses to convert the object
        to a format that can be easily serialized (e.g., dict, list, or primitive types).

        Returns:
            Any: A serializable representation of the object.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError
