const search = () => {
  const searchbox = document.getElementById("search-item").value.toUpperCase();
  const allemp = document.getElementById("allemp");
  const emp = document.querySelectorAll(".emp");
  const name = allemp.getElementsByTagName("h2");

  for (var i = 0; i < name.length; i++) {
    console.log(emp[0]);
  }
  // for (var i = 0; i < name.length; i++) {
  //   let match = emp[i].getElementByTagName("h2")[0];

  //   if (match) {
  //     let textvalue = match.textContent || match.innerHTML;

  //     if (textvalue.toUpperCase().indexOf(searchbox) > -1) {
  //       emp[i].style.display = "";
  //     } else {
  //       emp[i].style.display = "none";
  //     }
  //   }
  // }
};
