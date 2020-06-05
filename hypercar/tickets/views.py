from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from collections import deque


service_data = {
    'oil_queue': deque(),
    'tires_queue': deque(),
    'diagnostic_queue': deque(),
    'id': 0,
    'next_client': None
}

def if_next_client():
    return service_data['oil_queue'] or service_data['tires_queue'] or service_data['diagnostic_queue']

def next_number():
    if service_data['oil_queue']:
        return service_data['oil_queue'][0]
    elif service_data['tires_queue']:
        return service_data['tires_queue'][0]
    elif service_data['diagnostic_queue']:
        return service_data['diagnostic_queue'][0]

def delete_next():
    if service_data['oil_queue']:
        service_data['oil_queue'].popleft()
    elif service_data['tires_queue']:
        return service_data['tires_queue'].popleft()
    elif service_data['diagnostic_queue']:
        return service_data['diagnostic_queue'].popleft()

class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('h2>Welcome to the Hypercar Service!</h2>')

class MenuView(View):
    def get(self, request):
        menu = {'change_oil', 'inflate_tires', 'diagnostic'}
        return render(request, 'tickets/menu.html', {'menu': menu})

class GetTicketView(TemplateView):
    template_name = 'tickets/get_ticket.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        option = kwargs['option']
        if option == 'change_oil':
            service_data['id'] += 1
            context['ticket_number'] = service_data['id']
            context['minutes_to_wait'] = len(service_data['oil_queue']) * 2
            service_data['oil_queue'].append(service_data['id'])
        elif option == 'inflate_tires':
            service_data['id'] += 1
            context['ticket_number'] = service_data['id']
            context['minutes_to_wait'] = len(service_data['oil_queue']) * 2 + len(service_data['tires_queue']) * 5
            service_data['tires_queue'].append(service_data['id'])
        elif option == 'diagnostic':
            service_data['id'] += 1
            context['ticket_number'] = service_data['id']
            context['minutes_to_wait'] = len(service_data['oil_queue']) * 2 + len(service_data['tires_queue']) * 5 + len(service_data['diagnostic_queue']) * 30
            service_data['diagnostic_queue'].append(service_data['id'])
        return context

class ProcessingView(TemplateView):
    template_name = 'tickets/processing.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['oil_queue'] = len(service_data['oil_queue'])
        context['tires_queue'] = len(service_data['tires_queue'])
        context['diagnostic_queue'] = len(service_data['diagnostic_queue'])
        return context

    def post(self, request):
        if if_next_client():
            service_data['next_client'] = next_number()
            delete_next()
        else:
            service_data['next_client'] = None
        return redirect('/next')

class NextView(TemplateView):
    template_name = 'tickets/next.html'

    def get_context_data(self):
        context = super().get_context_data()
        if service_data['next_client']:
            context['number_of_ticket'] = service_data['next_client']
        return context