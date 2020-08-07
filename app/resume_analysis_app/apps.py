from django.apps import AppConfig


class ResumeAnalysisConfig(AppConfig):
    name = 'resume_analysis_app'

    def ready(self):
        import resume_analysis_app.signals
