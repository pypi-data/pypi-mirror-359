from semantic_kernel.functions import kernel_function

# from mps.integration.


class ReasoningPlugins:
    @kernel_function()
    def apply_cot_reasoning(): ...
    @kernel_function()
    def apply_tot_reasoning(): ...
    @kernel_function()
    def apply_aot_reasoning(): ...
