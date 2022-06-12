const allnavbtn=document.querySelectorAll('.navbtn');
allnavbtn[0].addEventListener("click",()=>{
    window.location.href="register";
});
allnavbtn[1].addEventListener("click",()=>{
    window.location.href="mail";
});
allnavbtn[2].addEventListener("click",()=>{
    window.location.href="leave";
});
allnavbtn[3].addEventListener("click",()=>{
    window.location.href="update" ;
});
allnavbtn[4].addEventListener("click",()=>{
    window.location.href="expenses";
});
allnavbtn[5].addEventListener("click",()=>{
    window.location.href="logout";
});