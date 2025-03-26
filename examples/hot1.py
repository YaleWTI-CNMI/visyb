

@plot_generator
def sample_scatter(testmod: modcont() = 3): # type: ignore
    return {ScatterPlot(testprop="hey")}

print("running hot1")
print(ScatterPlot)

add_plot(sample_scatter())