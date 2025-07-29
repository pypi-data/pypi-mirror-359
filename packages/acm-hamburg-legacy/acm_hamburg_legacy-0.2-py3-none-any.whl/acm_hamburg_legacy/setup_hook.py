def _setup_hook():
    from nerdd_module.preprocessing import register_pipeline

    from .preprocessing.acm_csp_pipeline import AcmCspPipeline
    from .preprocessing.acm_pipeline import AcmPipeline

    register_pipeline("acm", AcmPipeline())
    register_pipeline("acm_csp", AcmCspPipeline())
