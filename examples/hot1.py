
from visyb.processor import plot_generator, ScatterPlot, modcont, modcat, modbool


@plot_generator
def sample_scatter(testmod: modcont() = 3): # type: ignore
    return ScatterPlot(testprop="hey")

async def main():
    print("running hot1")
    print(ScatterPlot)

    # await add_plot(sample_scatter())

if __name__ == "__main":
    main()