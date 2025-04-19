import os, json, csv, smtplib
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from email.message import EmailMessage

# Create your views here.
