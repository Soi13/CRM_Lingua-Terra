#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use ConnectDB;
use JSON;
use Encode;
use Digest::MD5 qw(md5_hex);
use Time::Local; 

my $cgi = CGI->new;
my $SID;
my $method;

if (defined(cookie('SID'))) {
        $SID=cookie('SID');
        $SID=~s/\0//g; $SID=~s/\.\.//g; $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $method='cookies';
        }
elsif (defined(param('SID'))) {
        $SID=param('SID');
        $SID=~s/\0//g; $SID=~s/\.\.//g; $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $method='path';
        }
else {
        print "Location: http://localhost:6080\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $us_id=$sess->param('USER_ID');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

my $USER_LOGIN=param('LOGIN');
my $USER_NAME=param('FULL_NAME');
my $USER_STATUS=param('ADM');
my $TOP_SEKRETARIAT=param('TOP_SEKRETARIAT');
my $MAIN_SEKRETARIAT=param('MAIN_SEKRETARIAT');
my $GROUPS_SEKRETARIAT=param('GROUPS_SEKRETARIAT');
my $STUDENTS_SEKRETARIAT=param('STUDENTS_SEKRETARIAT');
my $TEACHERS_SEKRETARIAT=param('TEACHERS_SEKRETARIAT');
my $ROOMS_SEKRETARIAT=param('ROOMS_SEKRETARIAT');
my $CALENDAR_SEKRETARIAT=param('CALENDAR_SEKRETARIAT');
my $PERSONAL_CALENDAR_SEKRETARIAT=param('PERSONAL_CALENDAR_SEKRETARIAT');
my $FIRMS_SEKRETARIAT=param('FIRMS_SEKRETARIAT');
my $LINK_SEKRETARIAT=param('LINK_SEKRETARIAT');
my $SMS_SEKRETARIAT=param('SMS_SEKRETARIAT');
my $DOCUMENTS_SEKRETARIAT=param('DOCUMENTS_SEKRETARIAT');
my $USERS_SEKRETARIAT=param('USERS_SEKRETARIAT');
my $ZAYAV_SEKRETARIAT=param('ZAYAV_SEKRETARIAT');
my $RESERV_SEKRETARIAT=param('RESERV_SEKRETARIAT');
my $OPTIONS_SEKRETARIAT=param('OPTIONS_SEKRETARIAT');
my $TOP_FINANCE=param('TOP_FINANCE');
my $TRANSACTION_FINANCE=param('TRANSACTION_FINANCE');
my $SCHET_FACTUR_FINANCE=param('SCHET_FACTUR_FINANCE');
my $PRIH_ORDER_FINANCE=param('PRIH_ORDER_FINANCE');
my $IMPORT_FILES_BANK_FINANCE=param('IMPORT_FILES_BANK_FINANCE');
my $EXPORT_FILES_BANK_FINANCE=param('EXPORT_FILES_BANK_FINANCE');
my $OPTIONS_FINANCE=param('OPTIONS_FINANCE');
my $TOP_REGISTRATION=param('TOP_REGISTRATION');
my $FORMULARS_REGISTRATION=param('FORMULARS_REGISTRATION');
my $OPTIONS_REGISTRATIONS=param('OPTIONS_REGISTRATIONS');
my $TOP_E_LEARNING=param('TOP_E_LEARNING');
my $TESTS_E_LEARNING=param('TESTS_E_LEARNING');
my $LABELS_E_LEARNING=param('LABELS_E_LEARNING');
my $FILES_OF_BRANCH_E_LEARNING=param('FILES_OF_BRANCH_E_LEARNING');
my $FILES_E_LEARNING=param('FILES_E_LEARNING');
my $FILES_OF_TEACHERS_E_LEARNING=param('FILES_OF_TEACHERS_E_LEARNING');
my $TOP_MULTIMEDIATEKA=param('TOP_MULTIMEDIATEKA');
my $LIST_OF_POSITION_MULTIMEDIATEKA=param('LIST_OF_POSITION_MULTIMEDIATEKA');
my $OPTIONS_MULTIMEDIATEKA=param('OPTIONS_MULTIMEDIATEKA');
my $TOP_SUPERADMIN=param('TOP_SUPERADMIN');
my $BRANCHES_SUPERADMIN=param('BRANCHES_SUPERADMIN');
my $SUPERADMINISTRATORS_SUPERADMIN=param('SUPERADMINISTRATORS_SUPERADMIN');
my $OPTIONS_SUPERADMIN=param('OPTIONS_SUPERADMIN');
my $TOP_REPORTS=param('TOP_REPORTS');
my $REPORTS_REPORTS=param('REPORTS_REPORTS');
my $DEBTS_MONTH_REPORTS=param('DEBTS_MONTH_REPORTS');
my $PLAN_FACT_REPORTS=param('PLAN_FACT_REPORTS');
my $PLAN_FACT_REAL_PAYS_MONTH_REPORTS=param('PLAN_FACT_REAL_PAYS_MONTH_REPORTS');
my $TOP_E_JOURNAL=param('TOP_E_JOURNAL');
my $TOP_CONTROLLER=param('TOP_CONTROLLER');
my $TOP_ANKETS=param('TOP_ANKETS');
my $ANKETS_ANKETS=param('ANKETS_ANKETS');
my $LABELS_ANKETS=param('LABELS_ANKETS');
my $ABLE_DELETE_STUDENT_DOGOVOR=param('ABLE_DELETE_STUDENT_DOGOVOR');
my $ABLE_DELETE_ZAYAVKI=param('ABLE_DELETE_ZAYAVKI');
my $ABLE_DELETE_GROUP=param('ABLE_DELETE_GROUP');
my $ABLE_DEL_STUDENT_FROM_GROUP=param('ABLE_DEL_STUDENT_FROM_GROUP');
my $ABLE_DEL_LESSONS_FROM_GROUP=param('ABLE_DEL_LESSONS_FROM_GROUP');
my $ABLE_SET_BEGIN_STUDY=param('ABLE_SET_BEGIN_STUDY');
my $ABLE_CHANGE_SUMM_4_OPL=param('ABLE_CHANGE_SUMM_4_OPL');
my $ABLE_DEL_PERIOD_OF_PAYS=param('ABLE_DEL_PERIOD_OF_PAYS');
my $PASSW_DAYS_OF_LIVE=param('PASSW_DAYS_OF_LIVE');
my $id_user=param('id_x');
my $ABLE_SEND_SMS=param('ABLE_SEND_SMS');
my $STUDENTS_TEACHERS_REPORTS=param('STUDENTS_TEACHERS_REPORTS');
my $ABLE_ADD_PERIOD_OF_PAYS=param('ABLE_ADD_PERIOD_OF_PAYS');
my $STUDENTS_AGE_REPORTS=param('STUDENTS_AGE_REPORTS');
my $ABLE_ADD_EVENT=param('ABLE_ADD_EVENT');
my $ABLE_EDIT_EVENT=param('ABLE_EDIT_EVENT');
my $ABLE_DEL_EVENT=param('ABLE_DEL_EVENT');
my $ABLE_MOVE_STUDENTS_BETWEEN_GROUPS=param('ABLE_MOVE_STUDENTS_BETWEEN_GROUPS');
my $STUDENTS_DOGOVORS=param('STUDENTS_DOGOVORS');


$USER_LOGIN=~s/\0//g; $USER_LOGIN=~s/\.\.//g; $USER_LOGIN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$USER_NAME=~s/\0//g; $USER_NAME=~s/\.\.//g; $USER_NAME=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$USER_STATUS=~s/\0//g; $USER_STATUS=~s/\.\.//g; $USER_STATUS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TOP_SEKRETARIAT=~s/\0//g; $TOP_SEKRETARIAT=~s/\.\.//g; $TOP_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$MAIN_SEKRETARIAT=~s/\0//g; $MAIN_SEKRETARIAT=~s/\.\.//g; $MAIN_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$GROUPS_SEKRETARIAT=~s/\0//g; $GROUPS_SEKRETARIAT=~s/\.\.//g; $GROUPS_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$STUDENTS_SEKRETARIAT=~s/\0//g; $STUDENTS_SEKRETARIAT=~s/\.\.//g; $STUDENTS_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TEACHERS_SEKRETARIAT=~s/\0//g; $TEACHERS_SEKRETARIAT=~s/\.\.//g; $TEACHERS_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ROOMS_SEKRETARIAT=~s/\0//g; $ROOMS_SEKRETARIAT=~s/\.\.//g; $ROOMS_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$CALENDAR_SEKRETARIAT=~s/\0//g; $CALENDAR_SEKRETARIAT=~s/\.\.//g; $CALENDAR_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$PERSONAL_CALENDAR_SEKRETARIAT=~s/\0//g; $PERSONAL_CALENDAR_SEKRETARIAT=~s/\.\.//g; $PERSONAL_CALENDAR_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$FIRMS_SEKRETARIAT=~s/\0//g; $FIRMS_SEKRETARIAT=~s/\.\.//g; $FIRMS_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$LINK_SEKRETARIAT=~s/\0//g; $LINK_SEKRETARIAT=~s/\.\.//g; $LINK_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SMS_SEKRETARIAT=~s/\0//g; $SMS_SEKRETARIAT=~s/\.\.//g; $SMS_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$DOCUMENTS_SEKRETARIAT=~s/\0//g; $DOCUMENTS_SEKRETARIAT=~s/\.\.//g; $DOCUMENTS_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$USERS_SEKRETARIAT=~s/\0//g; $USERS_SEKRETARIAT=~s/\.\.//g; $USERS_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ZAYAV_SEKRETARIAT=~s/\0//g; $ZAYAV_SEKRETARIAT=~s/\.\.//g; $ZAYAV_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$RESERV_SEKRETARIAT=~s/\0//g; $RESERV_SEKRETARIAT=~s/\.\.//g; $RESERV_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$OPTIONS_SEKRETARIAT=~s/\0//g; $OPTIONS_SEKRETARIAT=~s/\.\.//g; $OPTIONS_SEKRETARIAT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TOP_FINANCE=~s/\0//g; $TOP_FINANCE=~s/\.\.//g; $TOP_FINANCE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TRANSACTION_FINANCE=~s/\0//g; $TRANSACTION_FINANCE=~s/\.\.//g; $TRANSACTION_FINANCE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SCHET_FACTUR_FINANCE=~s/\0//g; $SCHET_FACTUR_FINANCE=~s/\.\.//g; $SCHET_FACTUR_FINANCE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$PRIH_ORDER_FINANCE=~s/\0//g; $PRIH_ORDER_FINANCE=~s/\.\.//g; $PRIH_ORDER_FINANCE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$IMPORT_FILES_BANK_FINANCE=~s/\0//g; $IMPORT_FILES_BANK_FINANCE=~s/\.\.//g; $IMPORT_FILES_BANK_FINANCE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$EXPORT_FILES_BANK_FINANCE=~s/\0//g; $EXPORT_FILES_BANK_FINANCE=~s/\.\.//g; $EXPORT_FILES_BANK_FINANCE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$OPTIONS_FINANCE=~s/\0//g; $OPTIONS_FINANCE=~s/\.\.//g; $OPTIONS_FINANCE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TOP_REGISTRATION=~s/\0//g; $TOP_REGISTRATION=~s/\.\.//g; $TOP_REGISTRATION=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$FORMULARS_REGISTRATION=~s/\0//g; $FORMULARS_REGISTRATION=~s/\.\.//g; $FORMULARS_REGISTRATION=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$OPTIONS_REGISTRATIONS=~s/\0//g; $OPTIONS_REGISTRATIONS=~s/\.\.//g; $OPTIONS_REGISTRATIONS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TOP_E_LEARNING=~s/\0//g; $TOP_E_LEARNING=~s/\.\.//g; $TOP_E_LEARNING=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TESTS_E_LEARNING=~s/\0//g; $TESTS_E_LEARNING=~s/\.\.//g; $TESTS_E_LEARNING=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$LABELS_E_LEARNING=~s/\0//g; $LABELS_E_LEARNING=~s/\.\.//g; $LABELS_E_LEARNING=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$FILES_OF_BRANCH_E_LEARNING=~s/\0//g; $FILES_OF_BRANCH_E_LEARNING=~s/\.\.//g; $FILES_OF_BRANCH_E_LEARNING=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$FILES_E_LEARNING=~s/\0//g; $FILES_E_LEARNING=~s/\.\.//g; $FILES_E_LEARNING=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$FILES_OF_TEACHERS_E_LEARNING=~s/\0//g; $FILES_OF_TEACHERS_E_LEARNING=~s/\.\.//g; $FILES_OF_TEACHERS_E_LEARNING=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TOP_MULTIMEDIATEKA=~s/\0//g; $TOP_MULTIMEDIATEKA=~s/\.\.//g; $TOP_MULTIMEDIATEKA=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$LIST_OF_POSITION_MULTIMEDIATEKA=~s/\0//g; $LIST_OF_POSITION_MULTIMEDIATEKA=~s/\.\.//g; $LIST_OF_POSITION_MULTIMEDIATEKA=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$OPTIONS_MULTIMEDIATEKA=~s/\0//g; $OPTIONS_MULTIMEDIATEKA=~s/\.\.//g; $OPTIONS_MULTIMEDIATEKA=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TOP_SUPERADMIN=~s/\0//g; $TOP_SUPERADMIN=~s/\.\.//g; $TOP_SUPERADMIN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$BRANCHES_SUPERADMIN=~s/\0//g; $BRANCHES_SUPERADMIN=~s/\.\.//g; $BRANCHES_SUPERADMIN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SUPERADMINISTRATORS_SUPERADMIN=~s/\0//g; $SUPERADMINISTRATORS_SUPERADMIN=~s/\.\.//g; $SUPERADMINISTRATORS_SUPERADMIN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$OPTIONS_SUPERADMIN=~s/\0//g; $OPTIONS_SUPERADMIN=~s/\.\.//g; $OPTIONS_SUPERADMIN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TOP_REPORTS=~s/\0//g; $TOP_REPORTS=~s/\.\.//g; $TOP_REPORTS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$REPORTS_REPORTS=~s/\0//g; $REPORTS_REPORTS=~s/\.\.//g; $REPORTS_REPORTS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$DEBTS_MONTH_REPORTS=~s/\0//g; $DEBTS_MONTH_REPORTS=~s/\.\.//g; $DEBTS_MONTH_REPORTS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$PLAN_FACT_REPORTS=~s/\0//g; $PLAN_FACT_REPORTS=~s/\.\.//g; $PLAN_FACT_REPORTS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$PLAN_FACT_REAL_PAYS_MONTH_REPORTS=~s/\0//g; $PLAN_FACT_REAL_PAYS_MONTH_REPORTS=~s/\.\.//g; $PLAN_FACT_REAL_PAYS_MONTH_REPORTS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TOP_E_JOURNAL=~s/\0//g; $TOP_E_JOURNAL=~s/\.\.//g; $TOP_E_JOURNAL=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TOP_CONTROLLER=~s/\0//g; $TOP_CONTROLLER=~s/\.\.//g; $TOP_CONTROLLER=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TOP_ANKETS=~s/\0//g; $TOP_ANKETS=~s/\.\.//g; $TOP_ANKETS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ANKETS_ANKETS=~s/\0//g; $ANKETS_ANKETS=~s/\.\.//g; $ANKETS_ANKETS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$LABELS_ANKETS=~s/\0//g; $LABELS_ANKETS=~s/\.\.//g; $LABELS_ANKETS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_DELETE_STUDENT_DOGOVOR=~s/\0//g; $ABLE_DELETE_STUDENT_DOGOVOR=~s/\.\.//g; $ABLE_DELETE_STUDENT_DOGOVOR=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_DELETE_ZAYAVKI=~s/\0//g; $ABLE_DELETE_ZAYAVKI=~s/\.\.//g; $ABLE_DELETE_ZAYAVKI=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_DELETE_GROUP=~s/\0//g; $ABLE_DELETE_GROUP=~s/\.\.//g; $ABLE_DELETE_GROUP=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_DEL_STUDENT_FROM_GROUP=~s/\0//g; $ABLE_DEL_STUDENT_FROM_GROUP=~s/\.\.//g; $ABLE_DEL_STUDENT_FROM_GROUP=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_DEL_LESSONS_FROM_GROUP=~s/\0//g; $ABLE_DEL_LESSONS_FROM_GROUP=~s/\.\.//g; $ABLE_DEL_LESSONS_FROM_GROUP=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_SET_BEGIN_STUDY=~s/\0//g; $ABLE_SET_BEGIN_STUDY=~s/\.\.//g; $ABLE_SET_BEGIN_STUDY=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_CHANGE_SUMM_4_OPL=~s/\0//g; $ABLE_CHANGE_SUMM_4_OPL=~s/\.\.//g; $ABLE_CHANGE_SUMM_4_OPL=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_DEL_PERIOD_OF_PAYS=~s/\0//g; $ABLE_DEL_PERIOD_OF_PAYS=~s/\.\.//g; $ABLE_DEL_PERIOD_OF_PAYS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$PASSW_DAYS_OF_LIVE=~s/\0//g; $PASSW_DAYS_OF_LIVE=~s/\.\.//g; $PASSW_DAYS_OF_LIVE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$id_user=~s/\0//g; $id_user=~s/\.\.//g; $id_user=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_SEND_SMS=~s/\0//g; $ABLE_SEND_SMS=~s/\.\.//g; $ABLE_SEND_SMS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$STUDENTS_TEACHERS_REPORTS=~s/\0//g; $STUDENTS_TEACHERS_REPORTS=~s/\.\.//g; $STUDENTS_TEACHERS_REPORTS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_ADD_PERIOD_OF_PAYS=~s/\0//g; $ABLE_ADD_PERIOD_OF_PAYS=~s/\.\.//g; $ABLE_ADD_PERIOD_OF_PAYS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$STUDENTS_AGE_REPORTS=~s/\0//g; $STUDENTS_AGE_REPORTS=~s/\.\.//g; $STUDENTS_AGE_REPORTS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_ADD_EVENT=~s/\0//g; $ABLE_ADD_EVENT=~s/\.\.//g; $ABLE_ADD_EVENT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_EDIT_EVENT=~s/\0//g; $ABLE_EDIT_EVENT=~s/\.\.//g; $ABLE_EDIT_EVENT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_DEL_EVENT=~s/\0//g; $ABLE_DEL_EVENT=~s/\.\.//g; $ABLE_DEL_EVENT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ABLE_MOVE_STUDENTS_BETWEEN_GROUPS=~s/\0//g; $ABLE_MOVE_STUDENTS_BETWEEN_GROUPS=~s/\.\.//g; $ABLE_MOVE_STUDENTS_BETWEEN_GROUPS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$STUDENTS_DOGOVORS=~s/\0//g; $STUDENTS_DOGOVORS=~s/\.\.//g; $STUDENTS_DOGOVORS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#Перекодировка
Encode::from_to($USER_LOGIN,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($USER_NAME,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
###########################

##########Проверка на корректность логина.
if ($USER_LOGIN!~m/^[a-zA-Z0-9_]*$/is)
{
  my $ans="Введенный логин не корректен. В логине возможно применять только английские буквы, цифры и знак подчеркивания \"_\".";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;  
}
#############################################################

########Проверка на ввод логина
if (length($USER_LOGIN)==0)
{
  my $ans="Необходимо заполнить \"Логин\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка длинны логина
if (length($USER_LOGIN)>20)
{
  my $ans="Логин не может быть длиннее 20 символов!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод ФИО пользователя
if (length($USER_NAME)==0)
{
  my $ans="Необходимо заполнить \"ФИО пользователя\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на длинну ФИО пользователя
if (length($USER_NAME)>100)
{
  my $ans="\"ФИО пользователя\" не может быть длиннее 100 символов!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

##########Проверка на периода действия пароля.
if ($PASSW_DAYS_OF_LIVE!~m/^\d{1,2}$/is)
{
  my $ans="Период действия пароля может содержать только цифры и быть двухзначным.";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;  
}
#############################################################

########Проверка на ввод периода действия пароля
if (length($PASSW_DAYS_OF_LIVE)==0)
{
  my $ans="Поле \"Период действия пароля\" не может быть пустым!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на кол-во дней периода действия пароля
if (($PASSW_DAYS_OF_LIVE<20) || ($PASSW_DAYS_OF_LIVE>90))
{
  my $ans="Поле \"Период действия пароля\" не может быть меньше 20 и больше 90 дней!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

#Проверка на активацию разделов меню. Если главный раздел меню не активирован, то все его подразделы тоже деактивируем
#Раздел "Секретариат"
if (!defined($TOP_SEKRETARIAT))
{
  $MAIN_SEKRETARIAT=undef;
  $GROUPS_SEKRETARIAT=undef;
  $STUDENTS_SEKRETARIAT=undef;
  $TEACHERS_SEKRETARIAT=undef;
  $ROOMS_SEKRETARIAT=undef;
  $CALENDAR_SEKRETARIAT=undef;
  $PERSONAL_CALENDAR_SEKRETARIAT=undef;
  $FIRMS_SEKRETARIAT=undef;
  $LINK_SEKRETARIAT=undef;
  $SMS_SEKRETARIAT=undef;
  $DOCUMENTS_SEKRETARIAT=undef;
  $USERS_SEKRETARIAT=undef;
  $ZAYAV_SEKRETARIAT=undef;
  $RESERV_SEKRETARIAT=undef;
  $OPTIONS_SEKRETARIAT=undef;
}
#Раздел "Финансы"
if (!defined($TOP_FINANCE))
{
  $TRANSACTION_FINANCE=undef;
  $SCHET_FACTUR_FINANCE=undef;
  $PRIH_ORDER_FINANCE=undef;
  $IMPORT_FILES_BANK_FINANCE=undef;
  $EXPORT_FILES_BANK_FINANCE=undef;
  $OPTIONS_FINANCE=undef; 
}
#Раздел "Регистрация"
if (!defined($TOP_REGISTRATION))
{
  $FORMULARS_REGISTRATION=undef;
  $OPTIONS_REGISTRATIONS=undef;  
}
#Раздел "E-learning"
if (!defined($TOP_E_LEARNING))
{
  $TESTS_E_LEARNING=undef;
  $LABELS_E_LEARNING=undef; 
  $FILES_OF_BRANCH_E_LEARNING=undef;
  $FILES_E_LEARNING=undef;
  $FILES_OF_TEACHERS_E_LEARNING=undef;  
}
#Раздел "Мультимедиатека"
if (!defined($TOP_MULTIMEDIATEKA))
{
  $LIST_OF_POSITION_MULTIMEDIATEKA=undef;
  $OPTIONS_MULTIMEDIATEKA=undef;  
}
#Раздел "Суперадмин"
if (!defined($TOP_SUPERADMIN))
{
  $BRANCHES_SUPERADMIN=undef;
  $SUPERADMINISTRATORS_SUPERADMIN=undef;
  $OPTIONS_SUPERADMIN=undef;  
}
#Раздел "Отчеты"
if (!defined($TOP_REPORTS))
{
  $REPORTS_REPORTS=undef;
  $DEBTS_MONTH_REPORTS=undef; 
  $PLAN_FACT_REPORTS=undef;
  $PLAN_FACT_REAL_PAYS_MONTH_REPORTS=undef; 
  $STUDENTS_TEACHERS_REPORTS=undef;
  $STUDENTS_AGE_REPORTS=undef;
  $STUDENTS_DOGOVORS=undef;
}
#Раздел "Анкеты"
if (!defined($TOP_ANKETS))
{
  $ANKETS_ANKETS=undef;
  $LABELS_ANKETS=undef; 
} 
  
  #Вставляем самого пользователя
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="update usr set LOGIN=?, FULL_NAME=?, ADM=?, TOP_SEKRETARIAT=?, MAIN_SEKRETARIAT=?, GROUPS_SEKRETARIAT=?, STUDENTS_SEKRETARIAT=?, TEACHERS_SEKRETARIAT=?, ROOMS_SEKRETARIAT=?, CALENDAR_SEKRETARIAT=?, PERSONAL_CALENDAR_SEKRETARIAT=?, FIRMS_SEKRETARIAT=?, LINK_SEKRETARIAT=?, SMS_SEKRETARIAT=?, DOCUMENTS_SEKRETARIAT=?, USERS_SEKRETARIAT=?, ZAYAV_SEKRETARIAT=?, RESERV_SEKRETARIAT=?, OPTIONS_SEKRETARIAT=?, TOP_FINANCE=?, TRANSACTION_FINANCE=?, SCHET_FACTUR_FINANCE=?, PRIH_ORDER_FINANCE=?, IMPORT_FILES_BANK_FINANCE=?, EXPORT_FILES_BANK_FINANCE=?, OPTIONS_FINANCE=?, TOP_REGISTRATION=?, FORMULARS_REGISTRATION=?, OPTIONS_REGISTRATIONS=?, TOP_E_LEARNING=?, TESTS_E_LEARNING=?, LABELS_E_LEARNING=?, FILES_OF_BRANCH_E_LEARNING=?, FILES_E_LEARNING=?, FILES_OF_TEACHERS_E_LEARNING=?, TOP_MULTIMEDIATEKA=?, LIST_OF_POSITION_MULTIMEDIATEKA=?, OPTIONS_MULTIMEDIATEKA=?, TOP_SUPERADMIN=?, BRANCHES_SUPERADMIN=?, SUPERADMINISTRATORS_SUPERADMIN=?, OPTIONS_SUPERADMIN=?, TOP_REPORTS=?, REPORTS_REPORTS=?, DEBTS_MONTH_REPORTS=?, PLAN_FACT_REPORTS=?, PLAN_FACT_REAL_PAYS_MONTH_REPORTS=?, TOP_E_JOURNAL=?, TOP_CONTROLLER=?, TOP_ANKETS=?, ANKETS_ANKETS=?, LABELS_ANKETS=?, ABLE_DELETE_STUDENT_DOGOVOR=?, ABLE_DELETE_ZAYAVKI=?, ABLE_DELETE_GROUP=?, ABLE_DEL_STUDENT_FROM_GROUP=?, ABLE_DEL_LESSONS_FROM_GROUP=?, ABLE_SET_BEGIN_STUDY=?, ABLE_CHANGE_SUMM_4_OPL=?, ABLE_DEL_PERIOD_OF_PAYS=?, PASSW_DAYS_OF_LIVE=?, ABLE_SEND_SMS=?, STUDENTS_TEACHERS_REPORTS=?, ABLE_ADD_PERIOD_OF_PAYS=?, STUDENTS_AGE_REPORTS=?, ABLE_ADD_EVENT=?, ABLE_EDIT_EVENT=?, ABLE_DEL_EVENT=?, ABLE_MOVE_STUDENTS_BETWEEN_GROUPS=?, STUDENTS_DOGOVORS=? where ID=?";
  $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
  $sth1->execute($USER_LOGIN, $USER_NAME, $USER_STATUS, $TOP_SEKRETARIAT, $MAIN_SEKRETARIAT, $GROUPS_SEKRETARIAT, $STUDENTS_SEKRETARIAT, $TEACHERS_SEKRETARIAT, $ROOMS_SEKRETARIAT, $CALENDAR_SEKRETARIAT, $PERSONAL_CALENDAR_SEKRETARIAT, $FIRMS_SEKRETARIAT, $LINK_SEKRETARIAT, $SMS_SEKRETARIAT, $DOCUMENTS_SEKRETARIAT, $USERS_SEKRETARIAT, $ZAYAV_SEKRETARIAT, $RESERV_SEKRETARIAT, $OPTIONS_SEKRETARIAT, $TOP_FINANCE, $TRANSACTION_FINANCE, $SCHET_FACTUR_FINANCE, $PRIH_ORDER_FINANCE, $IMPORT_FILES_BANK_FINANCE, $EXPORT_FILES_BANK_FINANCE, $OPTIONS_FINANCE, $TOP_REGISTRATION, $FORMULARS_REGISTRATION, $OPTIONS_REGISTRATIONS, $TOP_E_LEARNING, $TESTS_E_LEARNING, $LABELS_E_LEARNING, $FILES_OF_BRANCH_E_LEARNING, $FILES_E_LEARNING, $FILES_OF_TEACHERS_E_LEARNING, $TOP_MULTIMEDIATEKA, $LIST_OF_POSITION_MULTIMEDIATEKA, $OPTIONS_MULTIMEDIATEKA, $TOP_SUPERADMIN, $BRANCHES_SUPERADMIN, $SUPERADMINISTRATORS_SUPERADMIN, $OPTIONS_SUPERADMIN, $TOP_REPORTS, $REPORTS_REPORTS, $DEBTS_MONTH_REPORTS, $PLAN_FACT_REPORTS, $PLAN_FACT_REAL_PAYS_MONTH_REPORTS, $TOP_E_JOURNAL, $TOP_CONTROLLER, $TOP_ANKETS, $ANKETS_ANKETS, $LABELS_ANKETS, $ABLE_DELETE_STUDENT_DOGOVOR, $ABLE_DELETE_ZAYAVKI, $ABLE_DELETE_GROUP, $ABLE_DEL_STUDENT_FROM_GROUP, $ABLE_DEL_LESSONS_FROM_GROUP, $ABLE_SET_BEGIN_STUDY, $ABLE_CHANGE_SUMM_4_OPL, $ABLE_DEL_PERIOD_OF_PAYS, $PASSW_DAYS_OF_LIVE, $ABLE_SEND_SMS, $STUDENTS_TEACHERS_REPORTS, $ABLE_ADD_PERIOD_OF_PAYS, $STUDENTS_AGE_REPORTS, $ABLE_ADD_EVENT, $ABLE_EDIT_EVENT, $ABLE_DEL_EVENT, $ABLE_MOVE_STUDENTS_BETWEEN_GROUPS, $STUDENTS_DOGOVORS, $id_user);

  $dbh1->disconnect;

  my $ans="Пользователь отредактирован успешно!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  ############################################################
  exit;


#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

}
else { print "Location: http://localhost:6080\n\n"; }
#############################################################

__END__
