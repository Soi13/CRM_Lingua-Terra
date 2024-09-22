#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use Digest::MD5 qw(md5_hex);
use Build_Menu qw(:DEFAULT $idd);

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

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $DOCUMENTS_SEKRETARIAT=$sess->param('DOCUMENTS_SEKRETARIAT');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

    if ($DOCUMENTS_SEKRETARIAT==1) #������� ����� �� ������ ������������ � ������ "���������".
    {
        #���������� �������� ����������� ��� ������ �� �� ��������
        open FF, "<txt_data/name_org.txt";
        my @name_org=<FF>;
        foreach my $str (@name_org)
        {
           $str=~s/\0//g;
           $str=~s/\.\.//g;
           $str=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        }
        close (FF) or die $!;
        #########################################

        print "Content-type: text/html\n\n";
        print <<HTML;
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset='windows-1251'>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>@name_org</title>
        <link rel="stylesheet" type="text/css" href="../CSS/easyui.css">
        <link rel="stylesheet" type="text/css" href="../CSS/icon.css">
        <link rel="stylesheet" type="text/css" href="../CSS/demo.css">
        <link rel="stylesheet" href="../CSS/styles.css">        
        
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script src="../JS/script.js"></script>
        <script src="../ckeditor/ckeditor.js"></script>
        <script src="../ckeditor/adapters/jquery.js"></script>        
               
        <script>
        function confirm1(){
        \$.messager.confirm('��������', '�� �������, ��� ���������� �����', function(r){
        if (r){
        //alert('confirmed: '+r);
        window.location.replace("/cgi-bin/exit.cgi?SID=$SID");
        }     });  }   </script>

        <!--Increae time of life session-->
        <script>
        \$(document).mouseup(function (e){
        \$.ajax({
                url: '/cgi-bin/session_alive.cgi?SID=$SID',
                success: function(){
                window.location.replace("http://localhost:6080")}
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
       
       <script type="text/javascript"> ////////////������ � ��������� ���������
        var url;
        function newTemplate(){
            \$('#dlg_template').dialog('open').dialog('center').dialog('setTitle','����� ������');
            \$('#fm').form('clear');      
            \$('#TEXT_OF_DOCUMENT').val(''); 
            \$('#SID').val('$SID');
            url = 'insert_template.cgi'; 
        }
        function editTemplate(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
	    \$('#dlg_template').dialog('open').dialog('center').dialog('setTitle','�������������� �������');
            \$('#fm').form('load',row);        
            \$('#id_x').val(row.ID);       
            \$('#SID').val('$SID');
            url = 'edit_template.cgi';                                          
            }
        }
        
        function saveTemplate() {
        var msg   = \$('#fm').serialize();
        \$.ajax({
          type: 'POST',
          url: url,
          data: msg,
          success: function(res) { \$.messager.alert('����������',res.result,'info'); if (res.result=="������ �������� �������!") {\$('#fm').form('clear'); \$('#dlg_template').dialog('close'); \$('#dg').datagrid('reload');} if (res.result=="������ �������������� �������!") {\$('#fm').form('clear'); \$('#dlg_template').dialog('close'); \$('#dg').datagrid('reload');}},
          error: function() {alert("did not work");}
        });        
       }
                
    </script>///////////////////////////////
	
	<script type="text/javascript"> ////////////������ � ��������� �������
        var url_order;
        function newTemplate_order(){
            \$('#dlg_template_order').dialog('open').dialog('center').dialog('setTitle','����� ������');
            \$('#fm_order').form('clear');      
            \$('#TEXT_OF_DOCUMENT_order').val(''); 
            \$('#SID_order').val('$SID');
            url_order = 'insert_template.cgi'; //?SID=$SID';
        }
        function editTemplate_order(){
            var row = \$('#dg_order').datagrid('getSelected');
            if (row){
	    \$('#dlg_template_order').dialog('open').dialog('center').dialog('setTitle','�������������� �������');
            \$('#fm_order').form('load',row);        
            \$('#id_x_order').val(row.ID);       
            \$('#SID_order').val('$SID');
            url_order = 'edit_template.cgi'; //?id_x='+row.ID+'&SID=$SID';                                          
            }
        }
        
        function saveTemplate_order() {
        var msg   = \$('#fm_order').serialize();
        \$.ajax({
          type: 'POST',
          url: url_order,
          data: msg,
          success: function(res) { \$.messager.alert('����������',res.result,'info'); if (res.result=="������ �������� �������!") {\$('#fm_order').form('clear'); \$('#dlg_template_order').dialog('close'); \$('#dg_order').datagrid('reload');} if (res.result=="������ �������������� �������!") {\$('#fm_order').form('clear'); \$('#dlg_template_order').dialog('close'); \$('#dg_order').datagrid('reload');}},
          error: function() {alert("did not work");}
        });        
       }
                
    </script>////////////////////////////////
    
    <script> //����������� ���������� ckeditor ������ TEXAREA
    \$(function(){                 
       \$('#TEXT_OF_DOCUMENT').ckeditor({uiColor:'#FDE0B0', fullPage:true});  
	   \$('#TEXT_OF_DOCUMENT_order').ckeditor({uiColor:'#FDE0B0', fullPage:true}); 
                 })
    </script>    
    
    
        </head>
 
 
        <body class="easyui-layout" onload="init()";>
        <!--������� DIV - ��������� -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px;"><h1 class="shd">@name_org</h1>
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

        <div id='cssmenu'>
        <ul>
HTML1
        #���������� � ��������� ����
        my $us_id=$sess->param('USER_ID'); #������ �� ������ USER_ID
        Build_Menu->menu($us_id, $SID); #� �������� ������� ��������� ID ������������ ��� ������ ����
        print <<HTML_e;
        </ul>
        </div>

        </div>
        <!--����� ����� DIV ������ ���� -->

        <!-- ������ DIV ������ ����������� -->
        <!--<div data-options="region:'east',split:true,title:'�����������'" style="width:30%;padding:1px;"></div> -->
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- ����������� DIV -������� ������� -->
        <div data-options="region:'center',title:'������� ������� - ���������. ������������: $formLogin'">

        <!-- ��������� Accordion � ������� ����� ����������� ��� ��������� -->        
        <div class="easyui-accordion" style="width:auto;height:100%">
        
        <div title="������� �������� ���������" style="overflow:auto; padding:10px;">        
        <table id="dg" class="easyui-datagrid" style="width:100%;height:100%"
        method="get"
        url="get_dogovor_templates.cgi?SID=$SID"
        toolbar="#toolbar"
        fitColumns="true" singleSelect="true" sortName="KIND_DOCUMENT" sortOrder="asc">

        <thead>
        <tr>
            <th field="ID" width="15" sortable="true" hidden="true">ID1</th>
            <th field="KND_DOC" width="50" sortable="true">��� ��������</th>                        
            <th field="NAIMENOVAN_DOCUMENT" width="100" sortable="true">������������ ���������</th>
            <th field="DESCRIPTION_DOCUMENT" width="100" sortable="true">�������� ���������</th>                        
            
        </tr>
        </thead>
        
        </table>
        <div id="toolbar">
        <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newTemplate()">�������� ������</a>
        <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editTemplate()">������������� ������</a>
        </div>
        </div>
        
        <div title="������� ������������ ���������" style="overflow:auto;padding:10px;">
        </div>
        
        <div title="������� ��������� ��" style="overflow:auto;padding:10px;">
        </div>
        
        <div title="������� ������ ��� ��������� ��" style="overflow:auto;padding:10px;">
        </div>
        
        <div title="������� �������" style="overflow:auto;padding:10px;">
        
        <table id="dg_order" class="easyui-datagrid" style="width:100%;height:100%"
        method="get"
        url="get_order_templates.cgi?SID=$SID"
        toolbar="#toolbar1"
        fitColumns="true" singleSelect="true" sortName="KIND_DOCUMENT" sortOrder="asc">

        <thead>
        <tr>
            <th field="ID" width="15" sortable="true" hidden="true">ID1</th>
            <th field="KND_DOC" width="50" sortable="true">��� ��������</th>                        
            <th field="NAIMENOVAN_DOCUMENT" width="100" sortable="true">������������ ���������</th>
            <th field="DESCRIPTION_DOCUMENT" width="100" sortable="true">�������� ���������</th>                        
            
        </tr>
        </thead>
        
        </table>
        <div id="toolbar1">
        <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newTemplate_order()">�������� ������</a>
        <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editTemplate_order()">������������� ������</a>
        </div>
        
        </div>	
		
		</div>
        <!-- ����� ��������� Accordion � ������� ����� ����������� ��� ��������� -->        
        
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
    
    <!-- ����� ���������� ������ ������� �������� -->    
    <div id="dlg_template" class="easyui-dialog" style="width:850px;height:650px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">�������� �������</div>
        <form id="fm" novalidate>
            <div class="fitem">
               	<label>��� ���������:</label>
               	<input name="TYPE_DOCUMENT" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_type_docs.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
            <div class="fitem">
               	<label>��� ���������:</label>
               	<input name="KIND_DOCUMENT" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_kind_docs.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
            <div class="fitem">
               	<label>������������ ���������:</label>
               	<input name="NAIMENOVAN_DOCUMENT" class="easyui-textbox" required missingMessage="������ ���� ���������� ���������">
	        </div>            
            <div class="fitem">
               	<label>�������� ���������:</label>
               	<input name="DESCRIPTION_DOCUMENT" class="easyui-textbox" data-options="multiline:true" style="height:100px">
	        </div>
	    <div class="fitem">
	        <label>���� ��� �������� ��������:</label>
	        <p>
	        <span class="lab"><a href="#">%�����_��������%</a></span> <span class="lab"><a href="#">%����_������_��������%</a></span> <span class="lab"><a href="#">%����_���������_��������%</a></span> <span class="lab"><a href="#">%���_���������%</a></span>
	        <span class="lab"><a href="#">%���_��������%</a></span> <span class="lab"><a href="#">%���_��������_��������%</a></span> <span class="lab"><a href="#">%���_�����%</a></span> <span class="lab"><a href="#">%���_�������%</a></span>
	        </p>       
	        </div>        
	    <div class="fitem">
               	<label>����� ���������:</label>
               	<textarea name="TEXT_OF_DOCUMENT" id="TEXT_OF_DOCUMENT" rows="10" cols="80">
               	</textarea>               
	        </div>
	        
	        <input name="SID" id="SID" type="hidden" value="">
	        <input name="id_x" id="id_x" type="hidden" value="">                 
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="saveTemplate()" style="width:100px">���������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_template').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ���������� ������ ������� �������� -->
	
	<!-- ����� ���������� ������ ������� ������ -->    
    <div id="dlg_template_order" class="easyui-dialog" style="width:850px;height:650px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_order" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">�������� �������</div>
        <form id="fm_order" novalidate>
            <div class="fitem">
               	<label>��� ���������:</label>
               	<input name="TYPE_DOCUMENT" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_type_docs.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
            <div class="fitem">
               	<label>��� ���������:</label>
               	<input name="KIND_DOCUMENT" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_kind_docs.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
            <div class="fitem">
               	<label>������������ ���������:</label>
               	<input name="NAIMENOVAN_DOCUMENT" class="easyui-textbox" required missingMessage="������ ���� ���������� ���������">
	        </div>            
            <div class="fitem">
               	<label>�������� ���������:</label>
               	<input name="DESCRIPTION_DOCUMENT" class="easyui-textbox" data-options="multiline:true" style="height:100px">
	        </div>
	    <div class="fitem">
	        <label>���� ��� �������� ��������:</label>
	        <p>
	        <span class="lab"><a href="#">%�����_��������%</a></span> <span class="lab"><a href="#">%����_������_��������%</a></span> <span class="lab"><a href="#">%����_���������_��������%</a></span> <span class="lab"><a href="#">%���_���������%</a></span>
	        <span class="lab"><a href="#">%���_��������%</a></span> <span class="lab"><a href="#">%����_��������_��������%</a></span> <span class="lab"><a href="#">%���_��������_��������%</a></span> <span class="lab"><a href="#">%���_�����%</a></span> <span class="lab"><a href="#">%���_�������%</a></span>
	        <span class="lab"><a href="#">%������ ���������_�����%</a></span> <span class="lab"><a href="#">%�����_��������_��������%</a></span> <span class="lab"><a href="#">%�����_��������_��������%</a></span> <span class="lab"><a href="#">%���_�����_�������_��������%</a></span>
	        <span class="lab"><a href="#">%�����_�����_�������_��������%</a></span> <span class="lab"><a href="#">%����_��������_��������%</a></span> <span class="lab"><a href="#">%�����_��������_��������%</a></span> <span class="lab"><a href="#">%�����_��������_��������%</a></span>
	        <span class="lab"><a href="#">%���_�����_�������_��������%</a></span> <span class="lab"><a href="#">%�����_�����_�������_��������%</a></span> <span class="lab"><a href="#">%��������� ��������%</a></span>
	        </p>       
	        </div>        
	    <div class="fitem">
               	<label>����� ���������:</label>
               	<textarea name="TEXT_OF_DOCUMENT" id="TEXT_OF_DOCUMENT_order" rows="10" cols="80">
               	</textarea>               
	        </div>
	        
	        <input name="SID" id="SID_order" type="hidden" value="">
	        <input name="id_x" id="id_x_order" type="hidden" value="">                 
        </form>
    </div>
    <div id="dlg-buttons_order">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="saveTemplate_order()" style="width:100px">���������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_template_order').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ���������� ������ ������� ������ -->
       
    
        </body>
        </html>
HTML_e

        #���������� ����� ����� ������
        $sess->atime(time());
        $sess->flush();
  } 
  else
  {
       &f_delete_session(); #������� ������
       
       print "Content-type: text/html\n\n";
       print <<HTML3;
       
       <!doctype html>
       <html>
       <head>
       <meta charset="windows-1251">
       <title>��� �������</title>

       <script type="text/javascript">
       setTimeout('location.replace("http://localhost:6080")', 3000);
       </script>

       <noscript>
       <meta http-equiv="refresh" content="3; url=http://localhost:6080">
       </noscript>

       <style type="text/css">
       body {
	       background-color: #4E5869;
       }
       .zagolovok {
	            font-family: "Times New Roman", Times, serif;
	            color: #FF0;	
       }
       </style>
       </head>

       <body>
       <h1 align="center" class="zagolovok"><strong>� ��� ��� ������� � ������� ������!</strong></h1>
       </body>
       </html>       
HTML3
   }   

#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         #������� ������
         $sess->delete();
         $sess->flush();
        }

#���������� SID � URL-������
sub f_add_sid {
        my $url=shift();
        if ($method eq 'path') {
                if (defined($SID) && $url !=~ m/SID=/) {
                        if ($url !=~ m/\?/) {
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