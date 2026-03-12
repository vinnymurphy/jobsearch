from .models import Job, Company

def database_stats(request):
    return {
        'total_jobs': Job.objects.count(),
        'total_companies': Company.objects.count(),
    }
