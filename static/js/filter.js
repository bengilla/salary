const search = () => {
  const searchbox = document.getElementById("search-item").value.toLowerCase();
  const listItems = document.querySelectorAll(".emp");

  listItems.forEach((item) => {
    let text = item.textContent;
    if (text.toLowerCase().includes(searchbox.toLowerCase())) {
      item.style.display = "";
    } else {
      item.style.display = "none";
    }
  });
};
