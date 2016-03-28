#!/usr/bin/env python
# encoding=utf-8


class StTraitBase(object):

    def __init__(self, name, kind):
        super(StTraitBase, self).__init__()
        self.name = name
        self.kind = kind
        self.metadatas = []


class StTraitSlot(StTraitBase):

    def __init__(self, name, kind):
        super(StTraitSlot, self).__init__(name, kind)
        self.slot_id = 0
        self.type_name = 0
        self.vindex = 0
        self.vkind = 0

    def __repr__(self):
        return '<StTraitSlot {0}>'.format(self.name)

    def detail(self, const_pool):
        name = const_pool.multinames[self.name]
        return '''<StTraitSlot {name}>
name: {name}
kind: 0x{self.kind:02x}
slot_id: {self.slot_id}
type_name: {self.type_name}
vindex: {self.vindex}
vkind: {self.vkind}
metadatas: {self.metadatas}
</StTraitSlot>
'''.format(
    name=name,
    self=self
)


class StTraitClass(StTraitBase):

    def __init__(self, name, kind):
        super(StTraitClass, self).__init__(name, kind)
        self.slot_id = 0
        self.classi = 0

    def __repr__(self):
        return '<StTraitClass {0}>'.format(self.name)

    def detail(self, const_pool):
        name = const_pool.multinames[self.name]
        return '''<StTraitClass {name}>
name: {name}
kind: 0x{self.kind:02x}
slot_id: {self.slot_id}
classi: {self.classi}
metadatas: {self.metadatas}
</StTraitClass>
'''.format(
    name=name,
    self=self
)


class StTraitFunction(StTraitBase):

    def __init__(self, name, kind):
        super(StTraitFunction, self).__init__(name, kind)
        self.disp_id = 0
        self.function = 0

    def __repr__(self):
        return '<StTraitFunction {0}>'.format(self.name)

    def detail(self, const_pool):
        name = const_pool.multinames[self.name]
        return '''<StTraitFunction {name}>
name: {name}
kind: 0x{self.kind:02x}
disp_id: {self.disp_id}
function: {self.function}
metadatas: {self.metadatas}
</StTraitFunction>
'''.format(
    name=name,
    self=self
)


class StTraitMethod(StTraitBase):

    def __init__(self, name, kind):
        super(StTraitMethod, self).__init__(name, kind)
        self.disp_id = 0
        self.method = 0

    def __repr__(self):
        return '<StTraitMethod {0}>'.format(self.name)

    def detail(self, const_pool):
        name = const_pool.multinames[self.name]
        return '''<StTraitMethod {name}>
name: {name}
kind: 0x{self.kind:02x}
disp_id: {self.disp_id}
method: {self.method}
metadatas: {self.metadatas}
</StTraitMethod>
'''.format(
    name=name,
    self=self
)


class TraitFactory(object):

    Trait_Slot = 0
    Trait_Method = 1
    Trait_Getter = 2
    Trait_Setter = 3
    Trait_Class = 4
    Trait_Function = 5
    Trait_Const = 6

    ATTR_Final = 1
    ATTR_Override = 2
    ATTR_Metadata = 4

    @classmethod
    def create(cls, stream):
        name = stream.readEncodedU32()
        kind = stream.readUI8()
        trait_type = kind & 0x0f
        if trait_type in (cls.Trait_Slot, cls.Trait_Const):
            trait = StTraitSlot(name, kind)
            trait.slot_id = stream.readEncodedU32()
            trait.type_name = stream.readEncodedU32()
            trait.vindex = stream.readEncodedU32()
            if trait.vindex != 0:
                trait.vkind = stream.readUI8()
        elif trait_type == cls.Trait_Class:
            trait = StTraitClass(name, kind)
            trait.slot_id = stream.readEncodedU32()
            trait.classi = stream.readEncodedU32()
        elif trait_type == cls.Trait_Function:
            trait = StTraitFunction(name, kind)
            trait.slot_id = stream.readEncodedU32()
            trait.function = stream.readEncodedU32()
        elif trait_type in (cls.Trait_Method, cls.Trait_Getter, cls.Trait_Setter):
            trait = StTraitMethod(name, kind)
            trait.disp_id = stream.readEncodedU32()
            trait.method = stream.readEncodedU32()
        else:
            raise Exception('Unknown trait type: {0:02x}'.format(trait_type))
        # attr
        if (kind>>4) & cls.ATTR_Metadata:
            metadata_count = stream.readEncodedU32()
            for k in range(metadata_count):
                trait.metadatas.append(stream.readEncodedU32())
        return trait
