from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .backend.research import Research
from .backend.report import Report
from uuid import uuid4

global_objects = {}

def magicRewrite(citation, student_paper, findings_to_insert):
    new_paper = student_paper.rewrite(findings_to_insert, citation)
    return new_paper

def handleRewrite(upl_res, upl_rep, selectedFindings):
    finding_results = upl_res.select(selected_items=selectedFindings)
    return finding_results

def citeMigration(research_paper_text, student_report_text, findings):
    uploaded_research = Research(text=research_paper_text)
    uploaded_research.read(findings)

    uploaded_report = Report(text=student_report_text)
    uploaded_research.set_student_report(student_report_text)

    return uploaded_research, uploaded_report

def index(request):
    if request.method == 'POST':
        research_paper = request.FILES.get('research_paper')
        student_report = request.FILES.get('student_report')
        findings = request.POST.get('findings')

        if research_paper:
            research_paper_text = research_paper.read().decode('utf-8')
        else:
            research_paper_text = None

        if student_report:
            student_report_text = student_report.read().decode('utf-8')
        else:
            student_report_text = None

        upl_res, upl_rep = citeMigration(research_paper_text, student_report_text, findings)

        # Generate a unique key for this request
        key = str(uuid4())
        # Store the objects in the global dictionary
        global_objects[key] = (upl_res, upl_rep)

        request.session['analysis_list'] = upl_res.get_analysis_list(include_relevancy=True)

        # Store the key in the session so we can access it later
        request.session['key'] = key

        return redirect('analysis')

    return render(request, 'index.html', {'numbers': list(range(3, 16))})

def analysis(request):
    if request.method == 'POST':
        selected_findings = request.POST.getlist('findings')

        # Retrieve the key from the session
        key = request.session.get('key')
        # Retrieve the objects using the key
        upl_res, upl_rep = global_objects.get(key, (None, None))

        research_findings = handleRewrite(upl_res, upl_rep, selected_findings)

        request.session['research_findings'] = research_findings

        return redirect('cite')

    analysis_list = request.session.get('analysis_list', [])

    return render(request, 'analysis.html', {'analysis_list': analysis_list})

def cite(request):
    if request.method == 'POST':
        citation = request.POST.get('citation')
        findings_to_insert = request.session.get('research_findings')

        # Retrieve the key from the session
        key = request.session.get('key')
        # Retrieve the objects using the key
        upl_res, upl_rep = global_objects.get(key, (None, None))

        new_report = magicRewrite("(" + citation + ")", upl_rep, findings_to_insert)

        request.session['new_report'] = new_report

        return redirect('magic')

    return render(request, 'cite.html')

def magic(request):
    new_report = request.session.get('new_report')
    return render(request, 'magic.html', {'new_report': new_report})
