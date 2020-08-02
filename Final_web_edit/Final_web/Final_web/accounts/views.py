from django.conf import settings
from django.contrib.auth import authenticate, logout, get_user_model, login as auth_login
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.shortcuts import render, HttpResponseRedirect, redirect, HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, FormView
from django.urls import reverse
from .forms  import SignUpForm, LoginForm, UserUpdateForm
from rest_framework.generics import (CreateAPIView)
from datetime import date

from .models import Patient, DoctorPatientRequest, Doctor, PatientRecords, DoctorComments, subscribers, pulses

User = get_user_model()


class SignUp(FormView):
    form_class = SignUpForm
    success_url = 'sign-in'
    template_name = 'accounts/sign-up.html'

    def form_valid(self, form):
        user = form.cleaned_data
        first_name = user.get('first_name')
        last_name = user.get('last_name')
        username = user.get('username')
        email = user.get('email')
        date_of_birth = user.get('date_of_birth')
        password = user.get('password')
        phone_number = user.get('phone_number')
        gender = user.get('gender')
        today = date.today()
        age = today.year - date_of_birth.year - (
                (today.day,today.month ) < ( date_of_birth.day,date_of_birth.month))



        _user = Doctor.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            phone_number=phone_number,
            age=age,
            gender=gender,
            is_doctor=True
        )

        return redirect("sign-in")


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = 'home'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if not user.is_doctor:
                return render(request, self.template_name, {
                    'form': self.get_form(),
                    'message_text': 'You are not authorized To login',
                    'message_level': 'danger'
                })
            else:
                auth_login(self.request, user)
                return redirect("myprofile")
        else:
            return render(request, self.template_name, {
                'form': self.get_form(),
                'message_text': 'Invalid Username or Password',
                'message_level': 'danger'
            })

        # if not user:
        #     return render(request, self.template_name, {
        #         'form': self.get_form(),
        #         'message_text': 'Invalid Username or Password',
        #         'message_level': 'danger'
        #     })
        #
        # if  not user.is_doctor:
        #     return render(request, self.template_name, {
        #         'form': self.get_form(),
        #         'message_text': 'You are not authorized To login',
        #         'message_level': 'danger'
        #     })
        #
        # auth_login(self.request, user)
        # return redirect("myprofile")


#  return redirect(reverse(settings.LOGIN_URL))


class LogoutView(View):

    def get(self, request):
        logout(request)
        response = redirect('/accounts/sign-in/')
        return response
    # return HttpResponseRedirect(settings.LOGIN_URL)


def home(request):
    return render(request, 'accounts/app.html')


def about_us(request):
    return render(request, 'accounts/about_us.html')


def myprofile(request):
    return render(request, 'accounts/profile.html')


def update_profile(request):
    user_form = UserUpdateForm(instance=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return render(request, 'accounts/profile.html')

    return render(request, 'accounts/updateprofile.html', {
        'user_form': user_form
    })


def patientsearch(request):
    all_request = DoctorPatientRequest.objects.all()
    all_patient = Patient.objects.all()
    user_id = request.user.id
    is_doctor = request.user.is_doctor

    if user_id and is_doctor:
        all_request = all_request.filter(doctor_id=user_id, status="accept")
        mypatient = []
        query = request.GET.get("q")
        for re in all_request:
            patient = all_patient.filter(id=re.patient_id)
            if patient and query:
                patient_search = patient.filter(username=query)
                mypatient += patient_search
            elif patient:
                mypatient += patient

        return render(request, 'accounts/patient.html', {'patients': mypatient})


def patient_detail(request, slug):
    global pulse_patient, previous_pulses
    patient_detail = Patient.objects.get(slug=slug)
    user_id = request.user.id
    # if request.method == "POST":
    #     comment = request.POST.get('doctorComment')
    #     DoctorComments.objects.create(patient_id=patient_detail.id, doctor_id=user_id, comment=comment)
    #     return redirect(reverse('patient_detail', kwargs={'slug': slug}))
    # old_comments = DoctorComments.objects.filter(patient=patient_detail, doctor_id=user_id)


    try:
        pulse_patient = pulses.objects.filter(patient_id=patient_detail.id).order_by('-id').first()
        puls_id = request.GET.get('puls_id')
        if puls_id:
            heartbeat = PatientRecords.objects.filter(pulse_id=puls_id)
            return render(request, 'accounts/patient_profile.html',
                          {'patient_detail': patient_detail, 'heartbeat': heartbeat,
                           'slug': slug})
        else:
            heartbeat = PatientRecords.objects.filter(pulse_id=pulse_patient.id)
            return render(request, 'accounts/patient_profile.html',
                          {'patient_detail': patient_detail, 'heartbeat': heartbeat,
                           'slug': slug,})
    except:
        return render(request, 'accounts/patient_profile.html', {'patient_detail': patient_detail})


def patient_pulse_detail(request, slug):
    patient_detail_pulse = Patient.objects.get(slug=slug)
    user_id = request.user.id
    if request.method == "POST":
        comment = request.POST.get('doctorComment')
        DoctorComments.objects.create(patient_id=patient_detail_pulse.id, doctor_id=user_id, comment=comment)
        return redirect(reverse('patient_pulse_detail', kwargs={'slug': slug}))
    old_comments = DoctorComments.objects.filter(patient=patient_detail_pulse, doctor_id=user_id)
    heart_beat_patient=pulses.objects.filter(patient_id=patient_detail_pulse.id)
    if heart_beat_patient is not None:
        if old_comments:
            return render(request, 'accounts/patient_pulse_profile.html',
                          {'patient_detail_pulse': patient_detail_pulse, 'heart_beat_patient': heart_beat_patient,'old_comments': old_comments})
        else:
            return render(request, 'accounts/patient_pulse_profile.html',
                          {'patient_detail_pulse': patient_detail_pulse, 'heart_beat_patient': heart_beat_patient,})

    else:
        if old_comments:
            return render(request, 'accounts/patient_pulse_profile.html',
                          {'patient_detail_pulse': patient_detail_pulse,
                           'old_comments': old_comments})
        else:
            return render(request, 'accounts/patient_pulse_profile.html',
                          {'patient_detail_pulse': patient_detail_pulse, })




    # puls_id = request.GET.get('puls_id')
    #     # if puls_id:
    #     #     heartbeat = PatientRecords.objects.filter(pulse_id=puls_id)
    #     #     return render(request, 'accounts/patient_profile.html',
    #     #                   {'patient_detail': patient_detail, 'heartbeat': heartbeat})











    # print(heart_beat_patient)
    # return render(request, 'accounts/patient_pulse_profile.html',
    #               {'patient_detail_pulse': patient_detail_pulse, 'heart_beat_patient': heart_beat_patient})
    # if heart_beat_patient:

    # else:
    #     return render(request, 'accounts/patient_pulse_profile.html',
    #                   {'patient_detail_pulse': patient_detail_pulse})










def subscribe(request):
    if request.method == "POST":
        user_email = request.POST.get('user_subscribe')
        subscribers.objects.create(email=user_email)
        return redirect('/')


def get_requests(request):
    all_request = DoctorPatientRequest.objects.all()
    all_patient = Patient.objects.all()
    user_id = request.user.id
    is_doctor = request.user.is_doctor

    if user_id and is_doctor:
        all_request = all_request.filter(doctor_id=user_id, status="NEW")
        final_requests = []
        for re in all_request:
            patient = all_patient.filter(id=re.patient_id)
            if patient:
                final_requests += patient

    return render(request, 'accounts/requests.html', {'requests': final_requests})


def accept_button(request):
    if request.method == 'GET':
        dd = request.GET.get('dd')
        if not dd:
            response = redirect('/accounts/requests/')
            return response

        else:
            all_request = DoctorPatientRequest.objects.all()
            patient_id_1 = Patient.objects.filter(id=dd)
            patient_id_11 = []
            patient_id_11 = patient_id_1
            isalm = patient_id_11

            user_id = request.user.id
            is_doctor = request.user.is_doctor
            if user_id and is_doctor:
                patient_requets_1 = all_request.filter(doctor_id=user_id, patient_id=dd,
                                                       status="NEW").values('id')
            if not patient_requets_1:
                response = redirect('/accounts/requests/')
                return response
            else:
                final_requests_1 = DoctorPatientRequest.objects.filter(pk=patient_requets_1[0].get('id')).update(
                    status='accept')

    all_request = DoctorPatientRequest.objects.all()
    all_patient = Patient.objects.all()
    user_id = request.user.id

    if user_id:
        all_request = all_request.filter(doctor_id=user_id, status="NEW")
        final_requests = []
        for re in all_request:
            patient = all_patient.filter(id=re.patient_id)
            if patient:
                final_requests += patient

    return render(request, 'accounts/requests.html', {'requests': final_requests})


def reject_button(request):
    if request.method == 'GET':
        dd = request.GET.get('dd')
        if not dd:
            response = redirect('/accounts/requests/')
            return response

        else:
            all_request = DoctorPatientRequest.objects.all()
            patient_id_1 = Patient.objects.filter(id=dd)
            patient_id_11 = []
            patient_id_11 = patient_id_1
            isalm = patient_id_11

            user_id = request.user.id
            if user_id:
                patient_requets_1 = all_request.filter(doctor_id=user_id, patient_id=dd,
                                                       status="NEW").values('id')
                if not patient_requets_1:
                    response = redirect('/accounts/requests/')
                    return response
                else:
                    final_requests_1 = DoctorPatientRequest.objects.filter(pk=patient_requets_1[0].get('id')).update(
                        status='reject')

    all_request = DoctorPatientRequest.objects.all()
    all_patient = Patient.objects.all()
    # query = request.GET.get("q")  # userdriver_id
    user_id = request.user.id

    if user_id:
        all_request = all_request.filter(doctor_id=user_id, status="NEW")
        final_requests = []
        for re in all_request:
            patient = all_patient.filter(id=re.patient_id)
            if patient:
                final_requests += patient

    return render(request, 'accounts/requests.html', {'requests': final_requests})

    # response = redirect('account/requests/')
    # return response
# return render(request, 'accounts/requests.html', {'req':final_requests })
