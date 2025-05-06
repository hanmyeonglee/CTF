<?php error_reporting(E_ALL); ini_set('display_errors', 1); ?>
<html>
    <head>
        <?php include_once './templates/head.html'; ?>
        <style>
            .main{ text-align:center; }
			.left{ 
				display: inline-block;
				width: 60%;
				text-align: left;
			}
        </style>
    </head>
    <body>
        <?php include_once './templates/nav.html'; ?>
        <?php

	    if( isset($_POST['submit']) && isset($_FILES['image']['tmp_name']) && isset($_POST['ext'])){
            $base_dir = "/tmp/";
            $ext = $_POST['ext'];

            if( preg_match("/^(png|jpg|jpeg)$/is", $ext) ){

                $content = file_get_contents($_FILES['image']['tmp_name']);
                if( preg_match( "/<\?php|<\?=|file_get_contents|scandir|closedir|readdir|move_uploaded_file/is", $content ) ){ die("no hack!"); }

                $random_name = bin2hex(random_bytes(10));
                $new_filename = $random_name . '.' . $ext;
                $file_path = $base_dir . $new_filename;

                if(move_uploaded_file($_FILES['image']['tmp_name'], $file_path) && file_exists($file_path) ){
                        @chmod(0777, $file_path);
                        echo "<script>alert('uploaded! redirecting..');location.href='/dir.php';</script>";
                }

            }
            else{
                echo "<script>alert('no hack! not allow extension.');</script>";
            }
        }

        ?>
        <div class="main">
            <div class="left">
                <form method="POST" action="/images.php" enctype="multipart/form-data">
                    <input type="file" name="image"><br>
                    <input type="text" name="ext" placeholder="extension : ( png | jpg | jpeg )" style="width:200px;">
                    <input type="submit" name="submit" value="이미지 올리기">
                </form>
            </div>
        </div>
    </body>
</html>
