"""
Base class for all custom ComfyUI nodes in Roslab SDK
"""

class RoslabBaseNode:
    """
    Base class for all Roslab custom ComfyUI nodes

    Provides common functionality and enforces consistent interface
    for Digital Twin process nodes.
    """

    # Category prefix for all Roslab nodes
    CATEGORY_PREFIX = "Roslab"

    # Return type prefix for custom data types
    RETURN_TYPE_PREFIX = "ROSLAB_"

    # Badge name shown in top right corner of nodes
    NAME = "pneumatic-kit"

    @classmethod
    def INPUT_TYPES(cls):
        """
        Define input types for the node.
        Must be overridden by subclasses.
        
        Returns:
            dict: Input specification
        """
        raise NotImplementedError("Subclasses must implement INPUT_TYPES")

    @classmethod
    def RETURN_TYPES(cls):
        """
        Define return types for the node.

        Returns:
            tuple: Output type names
        """
        return ("ANY",)

    @classmethod
    def RETURN_NAMES(cls):
        """
        Define names for return values (optional).

        Returns:
            tuple: Output names
        """
        return ("output",)

    @classmethod
    def FUNCTION(cls):
        """
        Name of the function to execute.

        Returns:
            str: Function name
        """
        return "execute"

    @classmethod
    def CATEGORY(cls):
        """
        Node category in ComfyUI menu.
        Must be overridden by subclasses.

        Returns:
            str: Category path
        """
        return f"{cls.CATEGORY_PREFIX}/Base"

    def execute(self, **kwargs):
        """
        Main execution function.
        Must be implemented by subclasses.
        
        Args:
            **kwargs: Node inputs
            
        Returns:
            tuple: Node outputs matching RETURN_TYPES
        """
        raise NotImplementedError("Subclasses must implement execute")

    def to_dict(self):
        """
        Serialize node configuration to dictionary.
        
        Returns:
            dict: Node configuration
        """
        return {
            "class": self.__class__.__name__,
            "category": self.__class__.CATEGORY,
            "inputs": self.INPUT_TYPES(),
            "outputs": {
                "types": self.__class__.RETURN_TYPES,
                "names": self.__class__.RETURN_NAMES
            }
        }

    def get_node_info(self):
        """
        Get metadata about this node for code generation.

        Returns:
            dict: Node metadata
        """
        return {
            "class": self.__class__.__name__,
            "category": self.__class__.CATEGORY,
            "inputs": self.INPUT_TYPES(),
            "outputs": {
                "types": self.__class__.RETURN_TYPES,
                "names": self.__class__.RETURN_NAMES
            }
        }


class RoslabConfigNode(RoslabBaseNode):
    """Base class for configuration nodes"""
    CATEGORY = "Rlab/pneumatic-kit/config"
    NAME = "pneumatic-kit"


class RoslabWidgetNode:
    """Base class for widget/UI nodes"""
    CATEGORY = "Rlab/pneumatic-kit/widgets"
    NAME = "pneumatic-kit"


class RoslabSystemNode:
    """Base class for system nodes"""
    CATEGORY = "Rlab/pneumatic-kit/systems"
    NAME = "pneumatic-kit"


class RoslabAssetNode:
    """Base class for asset nodes"""
    CATEGORY = "Rlab/pneumatic-kit/assets"
    NAME = "pneumatic-kit"
