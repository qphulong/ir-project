import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend import env
from backend import SemanticChunker
from llama_index.core.schema import Document as LlamaIndexDocument

"""
This script test functionality of semantic chunker.
Usage:
Can config the Chunker, see SemanticChunker class
The script should return splitted paragraphs of text in form of TextNode.
"""

semantic_chunker = SemanticChunker()

sample_document = LlamaIndexDocument(
    text="Russia is making gains at key spots along the frontlines of eastern and southeastern Ukraine, while unleashing wave after wave of aerial terror against Ukrainian cities. At the same time, Moscow is preparing to launch a counteroffensive in the southern Russian region of Kursk, the site of Kyiv’s only major military success this year. Moscow has deployed nearly 50,000 troops to Kursk, Ukrainian President Volodymyr Zelensky says, numbers that were boosted by recently arrived North Korean troops. “The Russians have the initiative across (the frontlines) right now, they have successfully exploited tactical gains and are reinforcing those tactical gains,” George Barros from the Institute for the Study of War told CNN. Barros, who leads the Russia and Geospatial Intelligence teams at the DC-based conflict monitoring group, said that Russia’s advantage on the battlefield makes it impossible for Ukraine to prepare for a possible counteroffensive. German Chancellor Olaf Scholz is photographed at the Chancellery in Berlin, Germany, on November 15, 2024. Related article Zelensky accuses German chancellor of opening ‘Pandora’s box’ with Putin. “The Russians are the ones taking action, and they’re forcing the Ukrainians to respond. That’s not a good thing, because you lose wars by constantly being on the defensive. … You just get boxed into a corner and you have to choose from a buffet of bad options,” Barros added. The situation is particularly dire around Kupiansk. The key northeastern city is once again at risk of falling to Russia after it was liberated by the Ukrainians in September 2022 following more than six months under Russian occupation. Kupiansk sits on the crossroads of two major supply roads and the Oskil river, which forms a major defensive feature in the area. Taking over Kupiansk would make it a lot easier for Russia to push further into the Kharkiv region. That would in turn put further pressure on Kharkiv, Ukraine’s second biggest city that has been pummeled by Russian drones and missiles on nearly daily basis. Russian state news agency Tass reported on Friday that Russian troops entered the outskirts of the city, although Ukrainian officials insisted Kupiansk remained under full control of their forces. At the same time, Ukraine is struggling to hold back Russian advances further south, around the city of Kurakhove, which has been surrounded from three sides for months. Earlier this week, Zelensky called the situation around Kurakhove “the most difficult area” of the frontline. But while Russia seems poised to take over the city in the coming days or weeks, Barros said this may not be a strategically significant loss for Kyiv, as it won’t significantly impact its ability to defend the wider region. Ukraine has put up a fierce fight in the area in recent months, even though it has lost some ground. Kurakhove lies some 40 kilometers (25 miles) south of Pokrovsk, a key logistical hub that has been in Russia’s crosshairs for many months. By late summer, Pokrovsk appeared almost certain to fall. Yet Kyiv’s forces have – for now – managed to repel Russia’s advances there, forcing Moscow to redraw its plans."
)

nodes = semantic_chunker.chunk_nodes_from_documents([sample_document])
for node in nodes:
    print(node.text,'\n\n')

