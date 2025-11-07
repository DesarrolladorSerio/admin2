# Test All Email Types
$recipient = 'brunoganora894@gmail.com'
$baseUrl = 'http://localhost:8004/api/notifications'

Write-Host '===== PRUEBA DE TODOS LOS EMAILS =====' -ForegroundColor Cyan
Write-Host 'Destinatario: ' -NoNewline; Write-Host $recipient -ForegroundColor Yellow
Write-Host ''

# Test 1: Welcome Email
Write-Host '[1/8] Email de Bienvenida...' -ForegroundColor Magenta
$body1 = @{ user_email='brunoganora894@gmail.com'; user_name='Bruno Ganora'; temp_password='test123' } | ConvertTo-Json
$r1 = Invoke-WebRequest -Uri "$baseUrl/welcome" -Method POST -Body $body1 -ContentType 'application/json'
Write-Host '   Enviado: ' -NoNewline -ForegroundColor Green; Write-Host (($r1.Content | ConvertFrom-Json).task_id)
Start-Sleep -Seconds 2

# Test 2: Password Reset
Write-Host '[2/8] Recuperacion de Password...' -ForegroundColor Magenta
$body2 = @{ user_email='brunoganora894@gmail.com'; user_name='Bruno Ganora'; reset_token='abc123'; reset_url='http://localhost/reset?token=abc123' } | ConvertTo-Json
$r2 = Invoke-WebRequest -Uri "$baseUrl/password-reset" -Method POST -Body $body2 -ContentType 'application/json'
Write-Host '   Enviado: ' -NoNewline -ForegroundColor Green; Write-Host (($r2.Content | ConvertFrom-Json).task_id)
Start-Sleep -Seconds 2

# Test 3: Reservation Confirmation
Write-Host '[3/8] Confirmacion de Reserva...' -ForegroundColor Magenta
$body3 = @{ user_email='brunoganora894@gmail.com'; user_name='Bruno Ganora'; reservation_data=@{ facility_name='Cancha de Futbol'; reservation_date='2024-11-15'; start_time='14:00'; end_time='16:00'; reservation_id=123 } } | ConvertTo-Json -Depth 5
$r3 = Invoke-WebRequest -Uri "$baseUrl/reservation/confirmation" -Method POST -Body $body3 -ContentType 'application/json'
Write-Host '   Enviado: ' -NoNewline -ForegroundColor Green; Write-Host (($r3.Content | ConvertFrom-Json).task_id)
Start-Sleep -Seconds 2

# Test 4: Reservation Reminder
Write-Host '[4/8] Recordatorio de Reserva...' -ForegroundColor Magenta
$body4 = @{ user_email='brunoganora894@gmail.com'; user_name='Bruno Ganora'; reservation_data=@{ facility_name='Sala Reuniones'; reservation_date='2024-11-07'; start_time='10:00'; end_time='12:00'; reservation_id=124 } } | ConvertTo-Json -Depth 5
$r4 = Invoke-WebRequest -Uri "$baseUrl/reservation/reminder" -Method POST -Body $body4 -ContentType 'application/json'
Write-Host '   Enviado: ' -NoNewline -ForegroundColor Green; Write-Host (($r4.Content | ConvertFrom-Json).task_id)
Start-Sleep -Seconds 2

# Test 5: Reservation Cancellation
Write-Host '[5/8] Cancelacion de Reserva...' -ForegroundColor Magenta
$body5 = @{ user_email='brunoganora894@gmail.com'; user_name='Bruno Ganora'; reservation_data=@{ facility_name='Gimnasio'; reservation_date='2024-11-20'; start_time='18:00'; end_time='20:00'; reservation_id=125; cancellation_date='2024-11-06' } } | ConvertTo-Json -Depth 5
$r5 = Invoke-WebRequest -Uri "$baseUrl/reservation/cancellation" -Method POST -Body $body5 -ContentType 'application/json'
Write-Host '   Enviado: ' -NoNewline -ForegroundColor Green; Write-Host (($r5.Content | ConvertFrom-Json).task_id)
Start-Sleep -Seconds 2

# Test 6: Document Uploaded
Write-Host '[6/8] Documento Subido...' -ForegroundColor Magenta
$body6 = @{ user_email='brunoganora894@gmail.com'; user_name='Bruno Ganora'; notification_type='uploaded'; document_data=@{ document_name='Cedula.pdf'; document_type='cedula'; upload_date='2024-11-06'; status='uploaded' } } | ConvertTo-Json -Depth 5
$r6 = Invoke-WebRequest -Uri "$baseUrl/document" -Method POST -Body $body6 -ContentType 'application/json'
Write-Host '   Enviado: ' -NoNewline -ForegroundColor Green; Write-Host (($r6.Content | ConvertFrom-Json).task_id)
Start-Sleep -Seconds 2

# Test 7: Document Approved
Write-Host '[7/8] Documento Aprobado...' -ForegroundColor Magenta
$body7 = @{ user_email='brunoganora894@gmail.com'; user_name='Bruno Ganora'; notification_type='approved'; document_data=@{ document_name='Licencia.pdf'; document_type='licencia'; approval_date='2024-11-06'; status='approved' } } | ConvertTo-Json -Depth 5
$r7 = Invoke-WebRequest -Uri "$baseUrl/document" -Method POST -Body $body7 -ContentType 'application/json'
Write-Host '   Enviado: ' -NoNewline -ForegroundColor Green; Write-Host (($r7.Content | ConvertFrom-Json).task_id)
Start-Sleep -Seconds 2

# Test 8: Document Rejected
Write-Host '[8/8] Documento Rechazado...' -ForegroundColor Magenta
$body8 = @{ user_email='brunoganora894@gmail.com'; user_name='Bruno Ganora'; notification_type='rejected'; document_data=@{ document_name='Certificado.pdf'; document_type='certificado'; rejection_date='2024-11-06'; rejection_reason='Documento ilegible'; status='rejected' } } | ConvertTo-Json -Depth 5
$r8 = Invoke-WebRequest -Uri "$baseUrl/document" -Method POST -Body $body8 -ContentType 'application/json'
Write-Host '   Enviado: ' -NoNewline -ForegroundColor Green; Write-Host (($r8.Content | ConvertFrom-Json).task_id)

Write-Host ''
Write-Host '===== COMPLETADO =====' -ForegroundColor Cyan
Write-Host 'Revisa tu email: brunoganora894@gmail.com' -ForegroundColor Yellow
Write-Host '(8 emails enviados)' -ForegroundColor Gray
