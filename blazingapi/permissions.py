class BasePermission:
    """
    Base class for all permission classes.
    """
    def __call__(self, *args, **kwargs):
        """
        Should raise an exception if the permission is not granted.
        """
