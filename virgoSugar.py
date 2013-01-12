#
#
# __     ___       ____
# \ \   / (_)_ __ / ___| ___
#  \ \ / /| | '__| |  _ / _ \
#   \ V / | | |  | |_| | (_) |
#    \_/  |_|_|   \____|\___/
#
# Some syntax sugar for virgo
#


from virgo import *


# Model[index]
# e.g. user = User[2]

MetaModel.__getitem__ = (
    lambda model, index: model.at(index).select().fetchone()
)


# Model[start, end]
# e.g. users = User[1:3]
# note:change this after between implement

def getslice(model, start, end):
    """Model[start, end]
    e.g. users = User[1:3]
    Produce: select * from user where user.id >= start and user.id  <= end
    """
    exprs = []

    if start:
        exprs.append(model.primarykey >= start)
    if end:
        exprs.append(model.primarykey <= end)
    return model.where(*exprs).select().fetchall()

MetaModel.__getslice__ = getslice
