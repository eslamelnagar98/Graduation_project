from rest_framework.decorators import api_view

from accounts.serializers import patient_register_serlizer, RequestSerializer, DoctorSerializer, Update_Patient, \
    RecordsSerializer, RequestSerializer_2, CommentsSerializer,heartbeatSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from django.contrib.auth import get_user_model

from django.shortcuts import render
from rest_framework.generics import (CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView, DestroyAPIView, ListAPIView,
                                     RetrieveAPIView)
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from django.db.models import Q
from accounts.models import Patient, DoctorPatientRequest, Doctor, PatientRecords, DoctorComments,pulses
from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
)

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from django.contrib.auth import login as django_login, logout as django_logout
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import generics, status

from rest_framework.filters import OrderingFilter, SearchFilter


class Register(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = patient_register_serlizer
    queryset = Patient.objects.all()


class update_user(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Patient.objects.all()
    serializer_class = Update_Patient
    lookup_field = 'slug'


class retrieve_user(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Patient.objects.all()
    serializer_class = patient_register_serlizer
    lookup_field = 'slug'


class retrieve_doctor(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DoctorSerializer

    def get_queryset(self):
        return Doctor.objects.filter(id=self.kwargs.get('doctor_id'))


class send_request(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DoctorSerializer
    filter_backends = [SearchFilter]
    search_fields = ('username')

    def get_queryset(self, *args, **kwargs):
        queryset_list = Doctor.objects.all()
        query = self.request.GET.get("username")
        if query:
            queryset_list = queryset_list.filter(
                Q(username__icontains=query)
            ).distinct()
        return queryset_list


#
class add_request(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RequestSerializer
    queryset = DoctorPatientRequest.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        DoctorPatientRequest.objects.filter(doctor_id=request.data['doctor'], patient_id=request.data['patient'],
                                            status='NEW').delete()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class accept_request(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RequestSerializer

    def get_queryset(self):
        return DoctorPatientRequest.objects.filter(doctor_id=self.kwargs.get('doctor_id'),
                                                   patient_id=self.kwargs.get('patient_id'), status='accept')


class accept_request_2(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RequestSerializer

    def get_queryset(self):
        return DoctorPatientRequest.objects.filter(doctor_id=self.kwargs.get('doctor_id'),
                                                   patient_id=self.kwargs.get('patient_id'), status='NEW')


class accept_request_3(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RequestSerializer

    def get_queryset(self):
        return DoctorPatientRequest.objects.filter(patient_id=self.kwargs.get('patient_id'), status='accept')


class cancel_request(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = DoctorPatientRequest.objects.all()

    def update(self, request, *args, **kwargs):
        # partial = kwargs.pop('partial', False)
        instance = self.get_object()
        instance.status = 'Cancel'
        instance.save()
        return Response(
            'Updated',
            status=status.HTTP_200_OK
        )



class recieve_records(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RecordsSerializer
    data  = serializer_class.data
    queryset = PatientRecords.objects.all()

    def create(self, request, *args, **kwargs):

        many = True if isinstance(request.data,list) else False
        data = request.data
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=False)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        pulses_id_1=pulses.objects.filter(patient=self.request.data[0]['patient']).order_by('-id').first()
        all_records = list(PatientRecords.objects.filter(pulse_id=pulses_id_1).order_by('-potential_energy'))


        pt_energy_all = []

        for i in all_records:
              pt_energy_all.append(i.potential_energy)

        f_12 = pt_energy_all[:12]
#         # print("f_12 - results")
#         # print(f_12)
        l_12 = pt_energy_all[-12:]
        # # print("l_12 - results")
        # # print(l_12)
        # print(pulses_id_1.id)
        avg_f_12=sum(f_12)/12.0
        heart_beat= avg_f_12/7.6

#         # print(all_records[0].time)

        x=pulses.objects.get(id=pulses_id_1.id)
        x.heart_beat=heart_beat
        x.time = all_records[0].time
        x.save()


        avg_l_12=sum(l_12)/12.0
        avg=avg_f_12/avg_l_12
        # print(avg_f_12)
        # print(avg_l_12)
        # print(avg)
        results =-1
        if (avg >= 1.4 and avg < 1.55) and (heart_beat >= 60 and heart_beat <= 100):
            results = 0
        elif avg <= 1.2 and (heart_beat >= 40 and heart_beat <= 59):
            results = 1
        elif (avg >= 1.4 and avg < 1.55) and (heart_beat >= 100 and heart_beat <= 160):
            results = 1
        elif (avg >= 1.4 and avg < 1.55) and (heart_beat >= 45 and heart_beat <= 100):
            results = 0
        elif (avg >= 1.4 and avg < 1.55) and (heart_beat >= 45 and heart_beat <= 100):
            results = 0
        elif (avg >= 1.4 and avg < 1.55) and (heart_beat >= 100 and heart_beat <= 250):
            results = 1
        elif (avg >= 1.4 and avg < 1.55) and (heart_beat >= 150 and heart_beat <= 175):
            results = 1
        elif (avg > 1.55) and (heart_beat >= 200):
            results = 1
        elif (avg >= 1.4 and avg < 1.55) and (heart_beat >= 40 and heart_beat <= 60):
            results = 1
        elif (avg >= 1.4 and avg < 1.55) and (heart_beat >= 60 and heart_beat <= 100):
            results = 0
        elif (avg >= 1.4 and avg < 1.55) and (heart_beat >= 60):
            results = 0
        elif (avg > 1.55) and (heart_beat >= 140 and heart_beat <= 280):
            results = 1
        elif (avg > 1.50) and (heart_beat >= 95 and heart_beat <= 150):
            results = 1
        elif (avg < 1.4) and (heart_beat >= 20 and heart_beat <= 40):
            results = 1
        elif (avg < 1.4) and (heart_beat >= 150 and heart_beat <= 220):
            results = 1
        elif (avg == 0) and (heart_beat == 0):
            results = 1
        print(results)
        return Response({'results': results,'heart_beat': heart_beat}, status=status.HTTP_201_CREATED, headers=headers)





class recieve_doctor_comment(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentsSerializer
    def get_queryset(self):
        return DoctorComments.objects.filter(patient_id=self.kwargs.get('patient_id'))



class recieve_heart_beat(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = heartbeatSerializer

    def get_queryset(self):
        return pulses.objects.filter(~Q(heart_beat=None),patient_id=self.kwargs.get('patient_id'))







