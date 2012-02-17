# -*- coding: utf-8 -*-
#
# Copyright (c) 2010-2012, Monash e-Research Centre
#   (Monash University, Australia)
# Copyright (c) 2010-2012, VeRSI Consortium
#   (Victorian eResearch Strategic Initiative, Australia)
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    *  Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    *  Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    *  Neither the name of the VeRSI, the VeRSI Consortium members, nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""
views.py

.. moduleauthor:: Kieran Spear <kispear@gmail.com>
.. moduleauthor:: Shaun O'Keefe <shaun.okeefe.0@gmail.com>

"""
import logging
import json

from django.http import HttpResponse
from django.template import Context
from django.shortcuts import render_to_response

from tardis.apps.sync.managers import manager, SyncManagerTransferError
from tardis.apps.sync.models import SyncedExperiment
from tardis.apps.sync.forms import FileTransferRequestForm
from tardis.tardis_portal import models

logger = logging.getLogger(__file__)

# provider api
def get_experiment(request):
    """ Request that an experiment be transferred from the provider
        to the consumer

    :param uid: a unique of the experiment generated by the  provider
    :rtype :class:'django.https.HttpResponse'
    """

    if request.method == 'POST':

        form = FileTransferRequestForm(request.POST)
        if not form.is_valid():
            return HttpResponse('ERROR', status=403)

        site_settings_url = request.POST['site_settings_url']
        # remote experiment id
        uid = request.POST['eid']

        ts = TransferService()
        try:
            ts.start_file_transfer(uid, site_settings_url)
        except TransferService.TransferError as detail:
            return HttpResponse('Transfer error: %s' % detail)
        except TransferService.InvalidUIDError:
            return HttpResponse('Transfer error: Experiment UID does not exist.', status=404)
        return HttpResponse('OK', status=200)

    else:
        form = FileTransferRequestForm()

    c = Context({'header': 'Register File Transfer Request',
                 'form': form})
    return render_to_response('tardis_portal/form_template.html', c)


def transfer_status(request, uid):
    """Request information about the status of the transfer of 
       an experiment.

    :param uid: a unique id of the experiment generated by the  provider
    :rtype :class:'django.https.HttpResponse'
    """
    ts = TransferService()
    try:
        json_dict = ts.get_status(uid)
    except TransferService.InvalidUIDError:
        json_dict = { 'error': 'invalid UID' }
    response = HttpResponse(json.dumps(json_dict), mimetype='application/json')
    response['Pragma'] = 'no-cache'
    response['Cache-Control'] = 'no-cache, must-revalidate'
    return response


# consumer api

def notify_experiment(request, uid):
    
    """Recive notification that an experiment has been ingested.

    :param uid: a unique id of the experiment generated by the provider
    :rtype :class:'django.https.HttpResponse'
    """
    # TODO
    exp = SyncedExperiment(uid=uid)
    exp.save()

