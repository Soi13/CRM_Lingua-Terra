#!/usr/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use Digest::MD5 qw(md5_hex);
use ConnectDB;

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
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:a0018982_fin",User=>"a0018982_oleg", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $num_dog=$sess->param('stud_num_dog');


#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {
        #���������� �������� ������ ������� ��� ������ �� �� ��������
        open FF, "<txt_data/pers_room.txt";
        my @pers_room=<FF>;
        foreach my $str (@pers_room)
        {
           $str=~s/\0//g;
           $str=~s/\.\.//g;
           $str=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        }
        close (FF) or die $!;
        #########################################
        
        my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth=$dbh->do("SET NAMES 'cp1251'");
        my $sql="select FIO from pupils where Num_dogovor like ?";
        $sth=$dbh->prepare($sql);
        $sth->execute($num_dog);

        #� ������ ���������� ����������� ������
        my @row = $sth->fetchrow_array;

        $dbh->disconnect;

        my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time); 
        $mon=$mon+1;
        $year=$year+1900;
        
        print "Content-type: text/html\n\n";
        print <<HTML;
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset='windows-1251'>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>@pers_room</title>
        <link rel="stylesheet" type="text/css" href="../CSS/easyui.css">
        <link rel="stylesheet" type="text/css" href="../CSS/icon.css">
        <link rel="stylesheet" type="text/css" href="../CSS/demo.css">">        
        <link rel="stylesheet" href="../CSS/styles.css">
        <link rel="stylesheet" type="text/css" href="../CSS/font_roboto/roboto.css"> 
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script src="../JS/script.js"></script>
        

        <script>
        function confirm1(){
        \$.messager.confirm('��������', '�� �������, ��� ���������� �����', function(r){
        if (r){
        //alert('confirmed: '+r);
        window.location.replace("/cgi-bin/exit.cgi?SID=$SID");
        }     });  }   </script>

        <!--Increase time of life session-->
        <script>
        \$(document).mouseup(function (e){
        \$.ajax({
                url: '/cgi-bin/session_alive.cgi?SID=$SID',
                success: function(){
                window.location.replace("https://students.linguaterra-soft.ru")}
                                });  });    </script>

        <script> //�������� ����� ����� ������
        function call() {
        var msg   = \$('#ff').serialize();
        \$.ajax({
          type: 'GET',
          url: 'change_psw.cgi?SID=$SID',
          data: msg,
          success: function(res) {alert(res.result); \$('#ff')[0].reset(); \$('#w').window('close');},
          error: function() {alert("did not work");}
        });

       }
       </script>
       
       
       <script>
       \$(function(){   
       //��������� � ������� ������ ��������� ��������� � ��������� �������
       \$('#list_of_students_visits').datagrid({
       title: '������ ��������� � �� ���������',
       method:'get',                                
       showHeader: true,       
       scrollbarSize: 0,
       striped: true,
       border: false,       
       singleSelect: true,
       url:'get_visits.cgi?SID=$SID',
       columns:[[
                  {field:'ID',title:'ID', hidden:true},
                  {field:'FIO',title:'<b>���</b>'},
                  {field:'PERIOD',title:'<b>������</b>'},                                                                                          
                  {field:'DAY1',title:'<b>1</b>', styler:cellStyler},
                  {field:'DAY2',title:'<b>2</b>', styler:cellStyler},
                  {field:'DAY3',title:'<b>3</b>', styler:cellStyler},
                  {field:'DAY4',title:'<b>4</b>', styler:cellStyler},
                  {field:'DAY5',title:'<b>5</b>', styler:cellStyler},
                  {field:'DAY6',title:'<b>6</b>', styler:cellStyler},
                  {field:'DAY7',title:'<b>7</b>', styler:cellStyler},
                  {field:'DAY8',title:'<b>8</b>', styler:cellStyler},
                  {field:'DAY9',title:'<b>9</b>', styler:cellStyler},
                  {field:'DAY10',title:'<b>10</b>', styler:cellStyler},
                  {field:'DAY11',title:'<b>11</b>', styler:cellStyler},
                  {field:'DAY12',title:'<b>12</b>', styler:cellStyler},
                  {field:'DAY13',title:'<b>13</b>', styler:cellStyler},
                  {field:'DAY14',title:'<b>14</b>', styler:cellStyler},
                  {field:'DAY15',title:'<b>15</b>', styler:cellStyler},
                  {field:'DAY16',title:'<b>16</b>', styler:cellStyler},
                  {field:'DAY17',title:'<b>17</b>', styler:cellStyler},
                  {field:'DAY18',title:'<b>18</b>', styler:cellStyler},
                  {field:'DAY19',title:'<b>19</b>', styler:cellStyler},
                  {field:'DAY20',title:'<b>20</b>', styler:cellStyler},
                  {field:'DAY21',title:'<b>21</b>', styler:cellStyler},
                  {field:'DAY22',title:'<b>22</b>', styler:cellStyler},
                  {field:'DAY23',title:'<b>23</b>', styler:cellStyler},
                  {field:'DAY24',title:'<b>24</b>', styler:cellStyler},
                  {field:'DAY25',title:'<b>25</b>', styler:cellStyler},
                  {field:'DAY26',title:'<b>26</b>', styler:cellStyler},
                  {field:'DAY27',title:'<b>27</b>', styler:cellStyler},
                  {field:'DAY28',title:'<b>28</b>', styler:cellStyler},
                  {field:'DAY29',title:'<b>29</b>', styler:cellStyler},
                  {field:'DAY30',title:'<b>30</b>', styler:cellStyler},
                  {field:'DAY31',title:'<b>31</b>', styler:cellStyler}                                                                                                                   
               ]]
         });       
         //////////////////////////////////////////	 
                                 
                                 
       //��������� � ������� ������ ��������� ��� � ��
       \$('#home_work').datagrid({
       method:'get',  
       title: '��������� ����/�������� �������',                              
       showHeader: true,       
       scrollbarSize: 0,
       striped: true,
       border: false,
       singleSelect: true,
       fitColumns: true,                                 
       url:'get_homework.cgi?&SID=$SID',
       columns:[[
                  {field:'ID',title:'ID', hidden:true},
                  {field:'DATE_LESSON',title:'<b>���� �������</b>'},
                  {field:'TOPIC',title:'<b>����</b>'},
                  {field:'HOME_WORK',title:'<b>��</b>'}                                                                                      
               ]]
           });       
          //////////////////////////////////////////    
          
        });                
        </script>
		
		<script>
        function cellStyler(value,row,index){
            if (value == '-'){
                return 'background-color:#ffee00;color:red;';
            }
            
            if (value == '+'){
                return 'background-color:#45f129;color:black;';
            }
        }
        </script>
		
		<script>
        function form_add_feedback() {
        var row = \$('#home_work').datagrid('getSelected'); 
        \$('#FEEDBACK').textbox('clear');   
        if (!row)
        {
          \$.messager.alert('��������','�� ������� ������� � �������� ����������� �������� �����. �������� ������� � ������ � ���������.','warning')
        }
        else
        {
          \$('#dlg_add_feedback').dialog('open').dialog('center').dialog('setTitle','���������� ������');
          \$('#topic_id').val(row.ID); 
          \$('#topic_name').val(row.TOPIC);
          \$('#date_lesson').val(row.DATE_LESSON);                     
        }  
                           
        }
        </script>
        
        <script>
        function add_feedback(){
        var msg = \$('#fm_add_feedback').serialize();
        \$.ajax({
          type: 'GET',
          url: 'add_feedback.cgi?SID=$SID',
          data: msg,
          success: function(res) { \$.messager.alert('����������',res.result,'info'); if (res.result=="����� ������� �������� � ���������!") {\$('#fm_add_feedback').form('clear'); \$('#dlg_add_feedback').dialog('close');}},          error: function() {alert("did not work");}
         });                
        }
        </script>
		
		<script>
        \$(function(){
        \$('#dg_student_feedback').datagrid({   
        method:'get',
        fitColumns: true,
        singleSelect:true,     
        columns:[[
                    {field:'ID',title:'ID',hidden:true},
                    {field:'TEXT_FEEDBACK',title:'�����',width:150},
                    {field:'DATETIME_CREATE',title:'���� ������',width:150}                    
                 ]]
            });
        });
        </script>
        
        <script>
        function show_feedback(){
             var row_id = \$('#home_work').datagrid('getSelected');        
             if (row_id){                
             \$('#window_student_feedback').window('open').dialog('center').dialog('setTitle','����� ��������');
             \$('#dg_student_feedback').datagrid({url: 'get_student_feedback.cgi?SID=$SID&id_lesson='+row_id.ID}); 
             //\$('#dg_student_feedback').datagrid('load', 'get_student_feedback.cgi?SID=$SID&id_lesson='+row_id.ID+'&nm_dogovor='+row_num_dog.Num_dogovor);
             //\$('#dg_student_feedback').datagrid('loadData',{url: 'get_student_feedback.cgi?SID=$SID&id_lesson='+row_id.ID+'&nm_dogovor='+row_num_dog.Num_dogovor});
             }
             else
             {
             \$.messager.alert('��������','���������� ������� ��������� ����!','warning');    
             }        
        }
        </script>
      
        
        </head>
        <body class="easyui-layout" onload="">
        <!--������� DIV - ��������� -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px;"><h1 class="shd">@pers_room</h1>
        <!--DIV � ������� ����� ������ ������-->
HTML
        #���������� ������, ������� ����� �� ������� ������
        open FF1, "<txt_data/buttons_panel.txt";
        my @buttons_panel=<FF1>;
        foreach my $str_but (@buttons_panel)
        {
           $str_but=~s/\0//g;
           $str_but=~s/\.\.//g;
           $str_but=~s/[<]*script[^>]*>.*[<]*\/script[>]*//i; #�� ���� ������ ������� ���� <script>
           $str_but=~s/SID=\$SID/SID=$SID/i; #����������� ���������� ���� SID � ������ ������ ���������� $SID. ��� �� �� �������������, �.�. ������ �������� �� ���������� �����.
        }
        close (FF1) or die $!;        
        print @buttons_panel;
        #########################################
        
        print <<HTML1;        
        <!--����� DIV � ������� ����� ������ ������-->
        </div>
        <!--����� ������� DIV - ��������� -->

        <!--����� DIV ������ ���� -->
        <div data-options="region:'west',split:false,title:'����'" style="width:205px;">
HTML1
        #���������� ����
        open FF2, "<txt_data/main_menu.txt";
        my @menu_panel=<FF2>;
        foreach my $str_menu (@menu_panel)
        {
           $str_menu=~s/\0//g;
           $str_menu=~s/\.\.//g;
           $str_menu=~s/[<]*script[^>]*>.*[<]*\/script[>]*//i; #�� ���� ������ ������� ���� <script>
           $str_menu=~s/SID=\$SID/SID=$SID/i; #����������� ���������� ���� SID � ������ ������ ���������� $SID. ��� �� �� �������������, �.�. ������ �������� �� ���������� �����.
        }
        close (FF2) or die $!;        
        print @menu_panel;
        #########################################       
        
        print <<HTML2;   
        </div>
        <!--����� ����� DIV ������ ���� -->

        <!-- ������ DIV ������ ����������� -->
        <!--<div data-options="region:'east',split:true,title:'�����������'" style="width:30%;padding:1px;">-->
        <!--</div>-->
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- ����������� DIV -������� ������� -->
        <div data-options="region:'center',title:'������� ������� - ������� � ��. �������: $row[0]'">

        <div id="ls" style="margin-left:10px; margin-top:10px;">
          <table id="list_of_students_visits" style="width:100%"></table>
        </div>
        <div id="ph" style="margin-top:20px; margin-left:10px;">
          <table id="home_work" class="easyui-datagrid" style="width:100%" toolbar="#dlg-buttons_feedback"></table>             
        </div>
		<div id="dlg-buttons_feedback">          
          <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="form_add_feedback()">�������� ����� � �������</a>
          <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="show_feedback()">�������� ������</a>           
        </div>
       

        </div>
        <!-- ����� ����������� DIV -������� ������� -->

        <!-- ����� ��������� ������ -->
        <div id="w" class="easyui-window" title="����� ������" data-options="modal:true,closed:true,iconCls:'icon-save'" style="width:370px;height:170px;padding:10px;">
        <form id="ff" action="javascript:void(null);" onsubmit="call()" method="post" enctype="multipart/form-data">
            <table>
                <tr>
                    <td>������� ������:</td>
                    <td><input id="curr_psw" name="curr_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>����� ������:</td>
                    <td><input name="new_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>��� ���:</td>
                    <td><input name="new_psw1" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td></td>
                    <td><input type="submit" value="�����������"></input></td>
                </tr>
            </table>
        </form>
    </div>
    <!-- ����� ����� ��������� ������ -->
	
	<!-- ����� ���������� ������ -->    
    <div id="dlg_add_feedback" class="easyui-dialog" style="width:550px;height:350px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_add_feedback" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">���������� ������</div>
        <form id="fm_add_feedback" novalidate>
           <div class="fitem">
               	<label>�����:</label>
               	<input id="FEEDBACK" name="FEEDBACK" class="easyui-textbox" data-options="multiline:true" style="height:200px; width:350px;">
	        </div>   
	        
	        <input name="topic_id" type="hidden" id="topic_id" value="" />
	        <input name="topic_name" type="hidden" id="topic_name" value="" />
	        <input name="date_lesson" type="hidden" id="date_lesson" value="" />
        </form>
    </div>
    <div id="dlg-buttons_add_feedback">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="add_feedback()" style="width:100px">��������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_add_feedback').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ���������� ������ -->
	
	<!-- ����� ����������� ������� ��������� -->    
    <div id="window_student_feedback" class="easyui-dialog" style="width:700px;height:550px;padding:10px 5px 0px 5px;"
            closed="true" modal="true", buttons="#dlg-buttons_feedback_st" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">            
        <table id="dg_student_feedback">     
    </div> 
    <div id="dlg-buttons_feedback_st">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#window_student_feedback').dialog('close')" style="width:90px">�������</a>
    </div>
    <!-- ����� ����� ����������� ������� ��������� -->   
    
    
        </body>
        </html>
HTML2

#���������� ����� ����� ������
$sess->atime(time());
$sess->flush();

#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://students.linguaterra-soft.ru');
         print "Set-Cookie: $cookies\n";
         #������� ������
         $sess->delete();
         $sess->flush();
        }

#���������� SID � URL-������
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
else { print "Location: https://students.linguaterra-soft.ru\n\n"; }