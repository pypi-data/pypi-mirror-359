class NotImplementedError(Exception):
    """
    Exception that is thrown when something so not yet implemented
    """

    def __init__(self, classOrMethodName):
        """
        Init an error with the name of the method/class that is not implemented yet.
        """
        self.name = classOrMethodName

    def __str__(self):
        return self.name + ": class or method is not yet implemented"


class AcmEnvVarError(Exception):
    """
    Exeption that is thrown when AcmEnvVariable is not set or path in AcmEnvVariable is invalid.
    """

    def __init__(self, envVar):
        """
        Init an error with the name of the AcmEnvVariable that is invalid.
        """
        self.name = envVar

    def __str__(self):
        if self.name == "$ACM_ORCA":
            return "Orca was not found. You propably did not set the path to your orca into the variable $ACM_ORCA.\nTo do so, please put the following line into your .bashrc:\nexport ACM_ORCA=PATH_TO_YOUR_ORCA_VERSION\nIf you are located in Hamburg you may enter in your .bashrc:export ACM_ORCA=/work/acm/share/applications/orca/orca_4_0_0_2_linux_x86-64/orcaqm"
        else:
            return (
                self.name + " variable not found. Please check if it was set correctly."
            )


class MoeLicenceNotFoundError(Exception):
    """
    Exception that is thrown when no MOE licence is found.
    """

    def __str__(self):
        return "MOE licence was not found"


class SmartsPatternFileAlreadyExistsError(Exception):
    """
    Exception that is thrown when a SMARTS pattern file already exists
    """

    def __init__(self, fileName):
        """
        Init an error with the name of the fileName that already exists
        """
        self.name = fileName

    def __str__(self):
        return self.name + ": already exists"


class UsingMulitprocessingWithLessThan2CoresError(Exception):
    """
    Exception that is thrown when a multiporcessing method is called with too less cores.
    """

    def __init__(self, method):
        """
        Init an error with the method name of the method that is used
        """
        self.method = method

    def __str__(self):
        return (
            self.name
            + " is used with less than 2 cores. Use the single core function or change the number of cores"
        )
