import tglib as tgl

tgs = tgl.load_ordered_edge_list("example_from_paper.tg")
stats = tgl.get_statistics(tgs)
print(stats)

