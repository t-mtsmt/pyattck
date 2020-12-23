from .configuration import Configuration
from .datasets import AttckDatasets


class Attck(object):

    """Interface to all MITRE ATT&CK frameworks.

    Currently, this class enables access to the Enterprise & PRE-ATT&CK
    frameworks with others coming soon.  To acccess each framework, use
    the following properties

        * enterprise
        * preattack

    This interface enables you to retrieve all properties within each
    item in the MITRE ATT&CK Enterprise Framework.

    The following categorical items can be accessed using this class:

        1. Tactics (Tactics are the phases defined by MITRE ATT&CK)
        2. Techniques (Techniques are the individual actions which can
            accomplish a tactic)
        3. Mitigations (Mitigations are recommendations to prevent or
            protect against a technique)
        4. Actors (Actors or Groups are identified malicious
            actors/groups which have been identified and documented by
            MITRE & third-parties)
        5. Tools (Tools are software used to perform techniques)
        6. Malwares (Malwares are specific pieces of malware used by
            actors (or in general) to accomplish a technique)

    You can also search the external dataset for external commands that
    are similar using the `search_commands` method.

        .. code-block:: python

            from pyattck import Attck

            attck = Attck()

            for search in attck.enterprise.search_commands('powershell'):
                print(search['technique'])
                print(search['reason_for_match'])

    Additionally, as of pyattck 2.0.0 you can now access additional
    datasets related to a technique. These datasets are
    [documented here](https://github.com/swimlane/pyattck/blob/master/generateattcks/README.md).

    Example:
        Once an Attck object is instantiated, you can access each object
        type as a list of objects (e.g. techniques, tactics, actors, etc.)

        You can iterate over each object list and access specific properties
        and relationship properties of each.

        The following relationship properties are accessible:
            1. Actors
                1. Tools used by the Actor or Group
                2. Malware used by the Actor or Group
                3. Techniques this Actor or Group uses
            2. Malwares
                1. Actor or Group(s) using this malware
                2. Techniques this malware is used with
            3. Mitigations
                1. Techniques related to a specific set of mitigation suggestions
            4. Tactics
                1. Techniques found in a specific Tactic (phase)
            5. Techniques
                1. Tactics a technique is found in
                2. Mitigation suggestions for a given technique
                3. Actor or Group(s) identified as using this technique
            6. Tools
                1. Techniques that the specified tool is used within
                2. Actor or Group(s) using a specified tool

            1. To iterate over a list, do the following:

            .. code-block:: python

               from pyattck import Attck

               attck = Attck()

               for technique in attck.enterprise.techniques:
                   print(technique.id)
                   print(technique.name)
                   print(technique.description)
                   # etc.
               for mitigation in attck.enterprise.mitigations:
                   print(mitigation.id)
                   print(mitigation.name)
                   print(mitigation.description)
                   # etc.

            2. To access relationship properties, do the following:

            .. code-block:: python

               from pyattck import Attck

               attck = Attck()

               for technique in attck.enterprise.techniques:
                   print(technique.id)
                   print(technique.name)
                   print(technique.description)
                   # etc.

                   for actor in technique.enterprise.actors:
                       print(actor.id)
                       print(actor.name)
                       print(actor.description)
                       # etc.

               for mitigation in attck.enterprise.mitigations:
                   print(mitigation.id)
                   print(mitigation.name)
                   print(mitigation.description)
                   # etc.

                   for technique in mitigation.enterprise.techniques:
                       print(technique.name)
                       print(technique.description)
                       # etc.

    Arguments:
        config_file_path (str, optional): Path to a yaml configuration file which contains two key value pairs. Defaults to None.
        data_path (str, optional): Path to store the external data locally on your system.  Defaults to current user path.
        force (bool, optional): Force reset configuration file and paths.  Defaults to False.

    Returns:
        [Attck]: Returns a Attck object that contains all data from MITRE ATT&CK Frameworks
    """

    __ENTERPRISE_ATTCK_JSON = None
    __MOBILE_ATTCK_JSON = None
    __PRE_ATTCK_JSON = None
    __ENTERPRISE_GENERATED_DATA_JSON = None
    __ENTERPRISE_NIST_DATA_JSON = None
    __tactics = None
    __techniques = None
    __mitigations = None
    __actors = None
    __tools = None
    __malwares = None

    def __init__(self, nested_subtechniques=True, config_file_path=None, data_path='~'):
        """
        The main entry point for pyattck.

        When instantiating an Attck object you can specify if you want the
        new subtechniques to be nested underneath their parent techniques
        or not.

        Setting nested_subtechniques to False will result in all techniques
        accessible under the techniques property. If using the default value
        of True, subtechniques will be accessible underneath
        technique.subtechniques.

        When instantiating an Attck object you can access either the
        Enterprise, PRE-ATT&CK, or Mobile MITRE Frameworks.  Specify
        one of the following properties to access the frameworks specific
        data:

            * enterprise
            * preattack
            * mobile

        You can specify an alternate location of a local copy of the
        following objects:

            1. config_file_path = Path to a yaml configuration file
                                  which contains two key value pairs
                Example content:

                    data_path: /Users/username/pyattck
                    enterprise:
                        filename: enterprise_attck.json
                        url: https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json
                    generated_data:
                        filename: enterprise_attck_dataset.json
                        url: https://raw.githubusercontent.com/swimlane/pyattck/master/generated_attck_data.json
                    mobile:
                        filename: mobile_attck.json
                        url: https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json
                    nist_800_53_rev4_controls:
                        filename: enterprise_attck_nist_800_53_rev4_controls.json
                        url: https://raw.githubusercontent.com/center-for-threat-informed-defense/attack-control-framework-mappings/master/frameworks/nist800-53-r4/stix/nist800-53-r4-controls.json
                    nist_data:
                        filename: enterprise_attck_nist_data.json
                        url: https://raw.githubusercontent.com/swimlane/pyattck/master/attck_to_nist_controls_data.json
                    preattck:
                        filename: preattack.json
                        url: https://raw.githubusercontent.com/mitre/cti/master/pre-attack/pre-attack.json

            2. data_path = The path to hold the external data locally on your system.
                           The default is your user home path.

        Args:
            config_file_path (str, optional): Path to a yaml configuration
                                              file which contains two key value pairs.
                                              Defaults to None.
            data_path (str, optional): Path to store the external data locally on your
                                       system.  Defaults to current user path.
            force (bool, optional): Force reset configuration file and paths.
                                    Defaults to False.
        """
        self.__nested_subtechniques = nested_subtechniques
        if config_file_path:
            Configuration.__CONFIG_FILE = config_file_path
        Configuration().set(data_path=data_path)
        self.__datasets = AttckDatasets()

    @property
    def enterprise(self):
        """
        Retrieve objects from the Enterprise MITRE ATT&CK Framework and
        additional generated data which provides additional context

        Returns:
            Enterprise: Returns an Enterprise object
        """
        self.__load_data()
        from .enterprise.enterprise import Enterprise
        return Enterprise(self.__ENTERPRISE_ATTCK_JSON, nested_subtechniques=self.__nested_subtechniques)

    @property
    def preattack(self):
        """
        Retrieve objects from the MITRE PRE-ATT&CK Framework

        Returns:
            PreAttack: Returns an PreAttack object
        """
        self.__load_data(type='preattack')
        from .preattck.preattck import PreAttck
        return PreAttck(self.__PRE_ATTCK_JSON)

    @property
    def mobile(self):
        """
        Retrieve objects from the MITRE Mobile ATT&CK Framework

        Returns:
            PreAttack: Returns an MobileAttack object
        """
        self.__load_data(type='mobile')
        from .mobile.mobileattck import MobileAttck
        return MobileAttck(self.__MOBILE_ATTCK_JSON)

    def update(self, enterprise=False, preattack=False, mobile=False):
        """
        Calling this method will force update / sync all datasets from
        external sources
        """
        if preattack:
            self.__load_data(type='preattack', force=True)
        if mobile:
            self.__load_data(type='mobile', force=True)
        if enterprise:
            self.__load_data(force=True)

    def __load_data(self, type='enterprise', force=False):
        if type == 'preattack':
            if not Attck.__PRE_ATTCK_JSON:
                Attck.__PRE_ATTCK_JSON = self.__datasets.get_data(
                    data_type='preattck', force=force
                )
        elif type == 'mobile':
            if not Attck.__MOBILE_ATTCK_JSON:
                Attck.__MOBILE_ATTCK_JSON = self.__datasets.get_data(
                    data_type='mobile', force=force
                )
        else:
            if not Attck.__ENTERPRISE_ATTCK_JSON:
                Attck.__ENTERPRISE_ATTCK_JSON = self.__datasets.get_data(
                    data_type='enterprise', force=force
                )
            if not Attck.__ENTERPRISE_GENERATED_DATA_JSON:
                Attck.__ENTERPRISE_GENERATED_DATA_JSON = self.__datasets.get_data(
                    data_type='generated_data', force=force
                )
            if not Attck.__ENTERPRISE_NIST_DATA_JSON:
                Attck.__ENTERPRISE_NIST_DATA_JSON = self.__datasets.get_data(
                    data_type='nist_data', force=force
                )
