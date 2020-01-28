# from .. import disk
# from . import Built
# from . import utilities
#
# CONSTRUCTORS = dict()
#
# class Constructor(Built):
#     # @staticmethod
#     # def _process_inputs(inputs):
#     #     script = inputs['script']
#     #     if type(script) is str:
#     #         pass
#     #     elif type(script) is type:
#     #         scriptFilename = script.__init__.__globals__['__file__']
#     #         script = disk.ToOpen(scriptFilename)()
#     #         inputs['script'] = script
#     def __init__(self, script = None, **kwargs):
#         imported = disk.local_import_from_str(script)
#         self.cls = imported.CLASS
#         self.defaultInps = utilities.get_default_kwargs(self.cls.__init__)
#         self.cls.typeHash = self.instanceHash
#         self.inputs = {'script': script}
#         self.inputsHash = make_hash(self.inputs)
#         self.instanceHash = self.inputsHash
#         self.hashID = wordhash.get_random_phrase(instanceHash)
#         super().__init__(**kwargs)
#     def __call__(self, **inputs):
#         inputs = {**self.defaultInps, **kwargs}
#         self.cls._process_inputs(inputs)
#
#         return self.cls(**inputs)
#
#         if _script is None:
#             cls.script = disk.ToOpen(cls.__init__.__globals__['__file__'])()
#         else:
#             cls.script = _script
#         cls.typeHash = make_hash(cls.script)
#         defaultInps = utilities.get_default_kwargs(cls.__init__)
#         inputs = {**defaultInps, **kwargs}
#         cls._process_inputs(inputs)
#         inputsHash = make_hash(inputs)
#         instanceHash = make_hash((cls.typeHash, inputsHash))
#         hashID = wordhash.get_random_phrase(instanceHash)
#         try:
#             obj = _get_prebuilt(hashID)
#         except BuiltNotCreatedYet:
#             obj = cls.__new__(cls)
#             obj.inputs = inputs
#             obj.inputsHash = inputsHash
#             obj.instanceHash = instanceHash
#             obj.hashID = hashID
#             obj.__init__(**inputs)
#         return obj
