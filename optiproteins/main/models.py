from django.db import models

# Create your models here.

from neomodel import (
    StructuredNode, StringProperty, ArrayProperty, config
)

class Protein(StructuredNode):
    entry = StringProperty(unique_index=True)
    entryName = StringProperty()
    proteinNames = StringProperty()
    organism = StringProperty()
    sequence = StringProperty()
    geneNames = ArrayProperty(StringProperty())   
    interPro  = ArrayProperty(StringProperty())
    ecNumbers = ArrayProperty(StringProperty())
