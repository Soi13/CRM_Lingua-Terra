#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
use CGI qw (:standart);
use CGI qw(:cgi);
#use CGI::Carp qw(fatalsToBrowser);
use JSON;
use ConnectDB;
use CGI::Session;

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

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

my $id=param('id');

my $cgi=CGI->new;
my @res;

my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sth1=$dbh->do("SET NAMES 'cp1251'");
my $sth2=$dbh->do("SET NAMES 'cp1251'");
my $sth3=$dbh->do("SET NAMES 'cp1251'");
my $sth4=$dbh->do("SET NAMES 'cp1251'");
my $sth5=$dbh->do("SET NAMES 'cp1251'");
my $sth6=$dbh->do("SET NAMES 'cp1251'");
my $sth7=$dbh->do("SET NAMES 'cp1251'");
my $sth8=$dbh->do("SET NAMES 'cp1251'");
my $sth9=$dbh->do("SET NAMES 'cp1251'");
my $sth10=$dbh->do("SET NAMES 'cp1251'");
my $sth11=$dbh->do("SET NAMES 'cp1251'");
my $sth12=$dbh->do("SET NAMES 'cp1251'");
my $sth13=$dbh->do("SET NAMES 'cp1251'");
my $sth14=$dbh->do("SET NAMES 'cp1251'");
my $sth15=$dbh->do("SET NAMES 'cp1251'");
my $sth16=$dbh->do("SET NAMES 'cp1251'");
my $sth17=$dbh->do("SET NAMES 'cp1251'");
my $sth18=$dbh->do("SET NAMES 'cp1251'");
my $sth19=$dbh->do("SET NAMES 'cp1251'");
my $sth20=$dbh->do("SET NAMES 'cp1251'");
my $sth21=$dbh->do("SET NAMES 'cp1251'");
my $sth22=$dbh->do("SET NAMES 'cp1251'");
my $sth23=$dbh->do("SET NAMES 'cp1251'");
my $sth24=$dbh->do("SET NAMES 'cp1251'");
my $sth25=$dbh->do("SET NAMES 'cp1251'");
my $sth26=$dbh->do("SET NAMES 'cp1251'");
my $sth27=$dbh->do("SET NAMES 'cp1251'");
my $sth28=$dbh->do("SET NAMES 'cp1251'");
my $sth29=$dbh->do("SET NAMES 'cp1251'");
my $sth30=$dbh->do("SET NAMES 'cp1251'");
my $sth31=$dbh->do("SET NAMES 'cp1251'");
my $sth32=$dbh->do("SET NAMES 'cp1251'");
my $sth33=$dbh->do("SET NAMES 'cp1251'");
my $sth34=$dbh->do("SET NAMES 'cp1251'");
my $sth35=$dbh->do("SET NAMES 'cp1251'");
my $sth36=$dbh->do("SET NAMES 'cp1251'");
my $sth37=$dbh->do("SET NAMES 'cp1251'");
my $sth38=$dbh->do("SET NAMES 'cp1251'");
my $sth39=$dbh->do("SET NAMES 'cp1251'");
my $sth40=$dbh->do("SET NAMES 'cp1251'");
my $sth41=$dbh->do("SET NAMES 'cp1251'");
my $sth42=$dbh->do("SET NAMES 'cp1251'");
my $sth43=$dbh->do("SET NAMES 'cp1251'");
my $sth44=$dbh->do("SET NAMES 'cp1251'");
my $sth45=$dbh->do("SET NAMES 'cp1251'");
my $sth46=$dbh->do("SET NAMES 'cp1251'");
my $sth47=$dbh->do("SET NAMES 'cp1251'");
my $sth48=$dbh->do("SET NAMES 'cp1251'");
my $sth49=$dbh->do("SET NAMES 'cp1251'");
my $sth50=$dbh->do("SET NAMES 'cp1251'");
my $sth51=$dbh->do("SET NAMES 'cp1251'");
my $sth52=$dbh->do("SET NAMES 'cp1251'");
my $sth53=$dbh->do("SET NAMES 'cp1251'");
my $sth54=$dbh->do("SET NAMES 'cp1251'");
my $sth55=$dbh->do("SET NAMES 'cp1251'");
my $sth56=$dbh->do("SET NAMES 'cp1251'");
my $sth57=$dbh->do("SET NAMES 'cp1251'");


my $sql="select 'Главный раздел-Секретариат' as 'name', IF(TOP_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql1="select 'Главная' as 'name', IF(MAIN_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql2="select 'Группы' as 'name', IF(GROUPS_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql3="select 'Студенты' as 'name', IF(STUDENTS_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql4="select 'Учителя' as 'name', IF(TEACHERS_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql5="select 'Кабинеты' as 'name', IF(ROOMS_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql6="select 'Календарь' as 'name', IF(CALENDAR_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql7="select 'Личный календарь' as 'name', IF(PERSONAL_CALENDAR_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql8="select 'Фирмы' as 'name', IF(FIRMS_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql9="select 'Связь' as 'name', IF(LINK_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql10="select 'СМС' as 'name', IF(SMS_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql11="select 'Документы' as 'name', IF(DOCUMENTS_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql12="select 'Пользователи' as 'name', IF(USERS_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql13="select 'Заявки' as 'name', IF(ZAYAV_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql14="select 'Резерв' as 'name', IF(RESERV_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql15="select 'Настройки' as 'name', IF(OPTIONS_SEKRETARIAT=1, 'Доступен', 'Не доступен') as 'value', 'Секретариат' as 'group' from usr where ID like ?";
my $sql16="select 'Главный раздел-Финансы' as 'name', IF(TOP_FINANCE=1, 'Доступен', 'Не доступен') as 'value', 'Финансы' as 'group' from usr where ID like ?";
my $sql17="select 'Транзакции' as 'name', IF(TRANSACTION_FINANCE=1, 'Доступен', 'Не доступен') as 'value', 'Финансы' as 'group' from urs where ID like ?";
my $sql18="select 'Счет-фактуры' as 'name', IF(SCHET_FACTUR_FINANCE=1, 'Доступен', 'Не доступен') as 'value', 'Финансы' as 'group' from usr where ID like ?";
my $sql19="select 'Приходный ордер' as 'name', IF(PRIH_ORDER_FINANCE=1, 'Доступен', 'Не доступен') as 'value', 'Финансы' as 'group' from usr where ID like ?";
my $sql20="select 'Импорт файлов из банка' as 'name', IF(IMPORT_FILES_BANK_FINANCE=1, 'Доступен', 'Не доступен') as 'value', 'Финансы' as 'group' from usr where ID like ?";
my $sql21="select 'Экспорт файлов в банк' as 'name', IF(EXPORT_FILES_BANK_FINANCE=1,'Доступен','Не доступен') as 'value', 'Финансы' as 'group' from usr where ID like ?";
my $sql22="select 'Настройки' as 'name', IF(OPTIONS_FINANCE=1,'Доступен','Не доступен') as 'value', 'Финансы' as 'group' from usr where ID like ?";
my $sql23="select 'Главный раздел-Регистрация' as 'name', IF(TOP_REGISTRATION=1,'Доступен','Не доступен') as 'value', 'Регистрация' as 'group' from usr where ID like ?";
my $sql24="select 'Формуляры' as 'name', IF(FORMULARS_REGISTRATION=1, 'Доступен', 'Не доступен') as 'value', 'Регистрация' as 'group' from usr where ID like ?";
my $sql25="select 'Настройки' as 'name', IF(OPTIONS_REGISTRATIONS=1, 'Доступен', 'Не доступен') as 'value', 'Регистрация' as 'group' from usr where ID like ?";
my $sql26="select 'Главный раздел-E-learning' as 'name', IF(TOP_E_LEARNING=1, 'Доступен', 'Не доступен') as 'value', 'E-learning' as 'group' from usr where ID like ?";
my $sql27="select 'Тесты' as 'name', IF(TESTS_E_LEARNING=1, 'Доступен', 'Не доступен') as 'value', 'E-learning' as 'group' from usr where ID like ?";
my $sql28="select 'Этикетки' as 'name', IF(LABELS_E_LEARNING=1, 'Доступен', 'Не доступен') as 'value', 'E-learning' as 'group' from usr where ID like ?";
my $sql29="select 'Файлы филиала' as 'name', IF(FILES_OF_BRANCH_E_LEARNING=1, 'Доступен', 'Не доступен') as 'value', 'E-learning' as 'group' from usr where ID like ?";
my $sql30="select 'Файлы' as 'name', IF(FILES_E_LEARNING=1, 'Доступен', 'Не доступен') as 'value', 'E-learning' as 'group' from usr where ID like ?";
my $sql31="select 'Файлы учителей' as 'name', IF(FILES_OF_TEACHERS_E_LEARNING=1, 'Доступен', 'Не доступен') as 'value', 'E-learning' as 'group' from usr where ID like ?";
my $sql32="select 'Главный раздел-Мультимедиатека' as 'name', IF(TOP_MULTIMEDIATEKA=1, 'Доступен', 'Не доступен') as 'value', 'Мультимедиатека' as 'group' from usr where ID like ?";
my $sql33="select 'Список позиций' as 'name', IF(LIST_OF_POSITION_MULTIMEDIATEKA=1, 'Доступен', 'Не доступен') as 'value', 'Мультимедиатека' as 'group' from usr where ID like ?";
my $sql34="select 'Настройки' as 'name', IF(OPTIONS_MULTIMEDIATEKA=1, 'Доступен', 'Не доступен') as 'value', 'Мультимедиатека' as 'group' from usr where ID like ?";
my $sql35="select 'Главный раздел-Администратор' as 'name', IF(TOP_SUPERADMIN=1, 'Доступен', 'Не доступен') as 'value', 'Администратор' as 'group' from usr where ID like ?";
my $sql36="select 'Филиалы' as 'name', IF(BRANCHES_SUPERADMIN=1, 'Доступен', 'Не доступен') as 'value', 'Администратор' as 'group' from usr where ID like ?";
my $sql37="select 'Суперадминистраторы' as 'name', IF(SUPERADMINISTRATORS_SUPERADMIN=1, 'Доступен', 'Не доступен') as 'value', 'Администратор' as 'group' from usr where ID like ?";
my $sql38="select 'Настройки' as 'name', IF(OPTIONS_SUPERADMIN=1, 'Доступен', 'Не доступен') as 'value', 'Администратор' as 'group' from usr where ID like ?";
my $sql39="select 'Главный раздел-Отчеты' as 'name', IF(TOP_REPORTS=1, 'Доступен', 'Не доступен') as 'value', 'Отчеты' as 'group' from usr where ID like ?";
my $sql40="select 'Должники на сегодня' as 'name', IF(REPORTS_REPORTS=1, 'Доступен', 'Не доступен') as 'value', 'Отчеты' as 'group' from usr where ID like ?";
my $sql41="select 'Должники за месяц' as 'name', IF(DEBTS_MONTH_REPORTS=1, 'Доступен', 'Не доступен') as 'value', 'Отчеты' as 'group' from urs where ID like ?";
my $sql42="select 'План-Факт по филиалам (за период)' as 'name', IF(PLAN_FACT_REPORTS=1, 'Доступен', 'Не доступен') as 'value', 'Отчеты' as 'group' from usr where ID like ?";
my $sql43="select 'Реальные поступления за месяц по филиалам' as 'name', IF(PLAN_FACT_REAL_PAYS_MONTH_REPORTS=1, 'Доступен', 'Не доступен') as 'value', 'Отчеты' as 'group' from usr where ID like ?";
my $sql44="select 'Главный раздел-Е-журнал' as 'name', IF(TOP_E_JOURNAL=1, 'Доступен', 'Не доступен') as 'value', 'Е-журнал' as 'group' from usr where ID like ?";
my $sql45="select 'Главный раздел-Контроллер' as 'name', IF(TOP_CONTROLLER=1, 'Доступен', 'Не доступен') as 'value', 'Контроллер' as 'group' from usr where ID like ?";
my $sql46="select 'Главный раздел-Анкеты' as 'name', IF(TOP_ANKETS=1, 'Доступен', 'Не доступен') as 'value', 'Анкеты' as 'group' from urs where ID like ?";
my $sql47="select 'Анкеты' as 'name', IF(ANKETS_ANKETS=1, 'Доступен', 'Не доступен') as 'value', 'Анкеты' as 'group' from usr where ID like ?";
my $sql48="select 'Этикетки' as 'name', IF(LABELS_ANKETS=1, 'Доступен', 'Не доступен') as 'value', 'Анкеты' as 'group' from usr where ID like ?";
my $sql49="select 'Удаление договора у студента' as 'name', IF(ABLE_DELETE_STUDENT_DOGOVOR=1, 'Доступен', 'Не доступен') as 'value', 'Доступные функции системы' as 'group' from usr where ID like ?";
my $sql50="select 'Удаление заявок' as 'name', IF(ABLE_DELETE_ZAYAVKI=1, 'Доступен', 'Не доступен') as 'value', 'Доступные функции системы' as 'group' from usr where ID like ?";
my $sql51="select 'Удаление групп' as 'name', IF(ABLE_DELETE_GROUP=1, 'Доступен', 'Не доступен') as 'value', 'Доступные функции системы' as 'group' from usr where ID like ?";
my $sql52="select 'Удаление студентов из группы' as 'name', IF(ABLE_DEL_STUDENT_FROM_GROUP=1, 'Доступен', 'Не доступен') as 'value', 'Доступные функции системы' as 'group' from usr where ID like ?";
my $sql53="select 'Удаление занятий/уроков из группы' as 'name', IF(ABLE_DEL_LESSONS_FROM_GROUP=1, 'Доступен', 'Не доступен') as 'value', 'Доступные функции системы' as 'group' from usr where ID like ?";
my $sql54="select 'Установка даты начала обучения' as 'name', IF(ABLE_SET_BEGIN_STUDY=1, 'Доступен', 'Не доступен') as 'value', 'Доступные функции системы' as 'group' from usr where ID like ?";
my $sql55="select 'Изменение суммы к оплате' as 'name', IF(ABLE_CHANGE_SUMM_4_OPL=1, 'Доступен', 'Не доступен') as 'value', 'Доступные функции системы' as 'group' from usr where ID like ?";
my $sql56="select 'Удаление периода для оплаты' as 'name', IF(ABLE_DEL_PERIOD_OF_PAYS=1, 'Доступен', 'Не доступен') as 'value', 'Доступные функции системы' as 'group' from usr where ID like ?";
my $sql57="select 'Период действия пароля' as 'name', concat(PASSW_DAYS_OF_LIVE, ' дн.') as 'value', 'Информация о пароле' as 'group' from usr where ID like ?";


$sth=$dbh->prepare($sql);
$sth1=$dbh->prepare($sql1);
$sth2=$dbh->prepare($sql2);
$sth3=$dbh->prepare($sql3);
$sth4=$dbh->prepare($sql4);
$sth5=$dbh->prepare($sql5);
$sth6=$dbh->prepare($sql6);
$sth7=$dbh->prepare($sql7);
$sth8=$dbh->prepare($sql8);
$sth9=$dbh->prepare($sql9);
$sth10=$dbh->prepare($sql10);
$sth11=$dbh->prepare($sql11);
$sth12=$dbh->prepare($sql12);
$sth13=$dbh->prepare($sql13);
$sth14=$dbh->prepare($sql14);
$sth15=$dbh->prepare($sql15);
$sth16=$dbh->prepare($sql16);
$sth17=$dbh->prepare($sql17);
$sth18=$dbh->prepare($sql18);
$sth19=$dbh->prepare($sql19);
$sth20=$dbh->prepare($sql20);
$sth21=$dbh->prepare($sql21);
$sth22=$dbh->prepare($sql22);
$sth23=$dbh->prepare($sql23);
$sth24=$dbh->prepare($sql24);
$sth25=$dbh->prepare($sql25);
$sth26=$dbh->prepare($sql26);
$sth27=$dbh->prepare($sql27);
$sth28=$dbh->prepare($sql28);
$sth29=$dbh->prepare($sql29);
$sth30=$dbh->prepare($sql30);
$sth31=$dbh->prepare($sql31);
$sth32=$dbh->prepare($sql32);
$sth33=$dbh->prepare($sql33);
$sth34=$dbh->prepare($sql34);
$sth35=$dbh->prepare($sql35);
$sth36=$dbh->prepare($sql36);
$sth37=$dbh->prepare($sql37);
$sth38=$dbh->prepare($sql38);
$sth39=$dbh->prepare($sql39);
$sth40=$dbh->prepare($sql40);
$sth41=$dbh->prepare($sql41);
$sth42=$dbh->prepare($sql42);
$sth43=$dbh->prepare($sql43);
$sth44=$dbh->prepare($sql44);
$sth45=$dbh->prepare($sql45);
$sth46=$dbh->prepare($sql46);
$sth47=$dbh->prepare($sql47);
$sth48=$dbh->prepare($sql48);
$sth49=$dbh->prepare($sql49);
$sth50=$dbh->prepare($sql50);
$sth51=$dbh->prepare($sql51);
$sth52=$dbh->prepare($sql52);
$sth53=$dbh->prepare($sql53);
$sth54=$dbh->prepare($sql54);
$sth55=$dbh->prepare($sql55);
$sth56=$dbh->prepare($sql56);
$sth57=$dbh->prepare($sql57);


$sth->execute($id);
$sth1->execute($id);
$sth2->execute($id);
$sth3->execute($id);
$sth4->execute($id);
$sth5->execute($id);
$sth6->execute($id);
$sth7->execute($id);
$sth8->execute($id);
$sth9->execute($id);
$sth10->execute($id);
$sth11->execute($id);
$sth12->execute($id);
$sth13->execute($id);
$sth14->execute($id);
$sth15->execute($id);
$sth16->execute($id);
$sth17->execute($id);
$sth18->execute($id);
$sth19->execute($id);
$sth20->execute($id);
$sth21->execute($id);
$sth22->execute($id);
$sth23->execute($id);
$sth24->execute($id);
$sth25->execute($id);
$sth26->execute($id);
$sth27->execute($id);
$sth28->execute($id);
$sth29->execute($id);
$sth30->execute($id);
$sth31->execute($id);
$sth32->execute($id);
$sth33->execute($id);
$sth34->execute($id);
$sth35->execute($id);
$sth36->execute($id);
$sth37->execute($id);
$sth38->execute($id);
$sth39->execute($id);
$sth40->execute($id);
$sth41->execute($id);
$sth42->execute($id);
$sth43->execute($id);
$sth44->execute($id);
$sth45->execute($id);
$sth46->execute($id);
$sth47->execute($id);
$sth48->execute($id);
$sth49->execute($id);
$sth50->execute($id);
$sth51->execute($id);
$sth52->execute($id);
$sth53->execute($id);
$sth54->execute($id);
$sth55->execute($id);
$sth56->execute($id);
$sth57->execute($id);


while ($data=$sth->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth1->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth2->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth3->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth4->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth5->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth6->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth7->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth8->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth9->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth10->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth11->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth12->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth13->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth14->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth15->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth16->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth17->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth18->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth19->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth20->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth21->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth22->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth23->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth24->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth25->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth26->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth27->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth28->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth29->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth30->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth31->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth32->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth33->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth34->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth35->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth36->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth37->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth38->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth39->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth40->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth41->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth42->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth43->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth44->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth45->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth46->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth47->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth48->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth49->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth50->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth51->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth52->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth53->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth54->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth55->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth56->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth57->fetchrow_hashref) {
push @res, $data;
}

$dbh->disconnect;

my $op=JSON->new->pretty(1);
my $json=$op->encode({ rows=> \@res, total => 4 });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
print $json;

#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://linguaterra-soft.ru');
         print "Set-Cookie: $cookies\n";
#         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

#Добавление SID к URL-адресу
sub f_add_sid {
        my $url=shift();
        if ($method eq 'path') {
                if (defined($SID) && $url !~ m/SID=/) {
                        if ($url !~ m/\?/) {
                                $url.="?SID=".$SID;
                                }
                        else {
                                $url.="&SID=".$SID;
                             }
                        }
                }
                return $url;
              }
}
else { print "Location: http://localhost:6080\n\n"; }


__END__