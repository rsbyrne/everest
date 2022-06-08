from everest.ptolemaic.essence import Essence


class InnerA(metaclass=Essence):
    ...


class InnerB(metaclass=Essence):
    ...


class InnerC(metaclass=Essence):
    ...


class A(metaclass=Essence):

    inner = _.mroclass(InnerA)


class B(metaclass=Essence):

    inner = InnerB


class C(B, A):

    inner = _.mroclass()

    # inner = _.mroclass(InnerC)

    # @_.mroclass
    # class inner(metaclass=Essence):
    #     foo = 1

    foo: int = 1
