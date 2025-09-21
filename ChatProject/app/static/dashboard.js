document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "/auth?mode=login";
    return;
  }

  try {
    const res = await fetch("/dashboard-data", {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!res.ok) throw new Error("Unauthorized");

    const data = await res.json();
    console.log(data);

    const avatarEl = document.getElementById("user-avatar");
    if (avatarEl) avatarEl.src = `https://ui-avatars.com/api/?name=${data.user.username}&background=random`;

    document.getElementById("app").innerHTML = `
      <div class="min-h-full">
        <nav class="bg-gray-800">
          <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between">
            <div class="flex items-center">
              <div class="shrink-0 text-white font-bold">Welcome, ${data.user.username}</div>
              <div class="ml-10 flex space-x-4">
                ${data.navigation.map(nav => `
                  <a href="${nav.href}" class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-white/5 hover:text-white">${nav.name}</a>
                `).join("")}
                <a href="#" id="find-match-btn" class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-white/5 hover:text-white">Find Match</a>
              </div>
            </div>
          </div>
        </nav>
        <header class="bg-white shadow-sm">
          <div class="mx-auto max-w-7xl px-4 py-6">
            <h1 class="text-3xl font-bold tracking-tight text-gray-900">Dashboard</h1>
          </div>
        </header>
        <main class="mx-auto max-w-7xl px-4 py-6">
          <p class="text-gray-700">Hello ${data.user.username}, welcome back 🎉</p>

          <!-- Match Finder Section -->
          <div id="match-section" class="mt-6 hidden">
            <h2 class="text-xl font-semibold mb-2">Find a Match</h2>
            <p>Enter at least 3 skills to find users with similar skills:</p>
            <div class="grid grid-cols-3 gap-2 mb-2">
              <input type="text" placeholder="Skill 1" class="match-skill p-1 border rounded"/>
              <input type="text" placeholder="Skill 2" class="match-skill p-1 border rounded"/>
              <input type="text" placeholder="Skill 3" class="match-skill p-1 border rounded"/>
            </div>
            <button id="search-matches" class="px-3 py-1 bg-green-500 text-white rounded">Search</button>
            <div id="match-results" class="mt-4"></div>
          </div>

          <!-- Chat Section -->
          <div id="chat-section" class="mt-6 hidden">
            <h2 class="text-xl font-semibold mb-2">Чати</h2>
            <div id="chat-list" class="space-y-2"></div>
          </div>
        </main>
      </div>
    `;

    // Show Match Finder
    const matchBtn = document.getElementById("find-match-btn");
    matchBtn.addEventListener("click", (e) => {
      e.preventDefault();
      document.getElementById("match-section").classList.toggle("hidden");
    });

    // Search matches
    const searchBtn = document.getElementById("search-matches");
    searchBtn.addEventListener("click", async () => {
      const skills = Array.from(document.querySelectorAll(".match-skill"))
                          .map(input => input.value.trim())
                          .filter(Boolean);
      if (skills.length < 3) {
        alert("Please enter at least 3 skills");
        return;
      }

      try {
        const res = await fetch("/matches/find", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify({ skills })
        });
        if (!res.ok) throw new Error("Failed to fetch matches");
        const matches = await res.json();
        const resultEl = document.getElementById("match-results");
        resultEl.innerHTML = "";

        matches.matches.forEach(m => {
          const div = document.createElement("div");
          div.className = "p-2 border rounded mb-2 flex justify-between items-center";
          div.innerHTML = `<div><strong>${m.username}</strong><br><small>Shared Skills: ${m.common_skills.join(", ")}</small></div>`;

          const btn = document.createElement("button");
          btn.textContent = "Message";
          btn.className = "px-2 py-1 bg-blue-500 text-white rounded";
          btn.addEventListener("click", async () => {
            try {
              await fetch(`/matches/save/${m.user_id}`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` }
              });
              alert(`Match saved! You can now chat with ${m.username}`);
              document.getElementById("chat-section").classList.remove("hidden");
            } catch (err) {
              console.error(err);
              alert("Failed to save match");
            }
          });

          div.appendChild(btn);
          resultEl.appendChild(div);
        });

      } catch (err) {
        console.error(err);
        alert("Error searching matches");
      }
    });

    // Chat link handling
    const chatLink = Array.from(document.querySelectorAll("a")).find(a => a.textContent === "Чати");
    if (chatLink) {
      chatLink.addEventListener("click", async (e) => {
        e.preventDefault();
        document.getElementById("chat-section").classList.remove("hidden");
      });
    }

document.getElementById("add-skill-btn").addEventListener("click", async () => {
  const skillName = document.getElementById("new-skill-input").value.trim();
  if (!skillName) return alert("Введіть назву навички");

  const token = localStorage.getItem("access_token");

  try {
    // Try to create the skill
    let skill;
    const createRes = await fetch("/skills/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ name: skillName })
    });

    if (createRes.ok) {
      skill = await createRes.json();
    } else if (createRes.status === 400) {
      // Skill already exists: fetch user's skills to get its ID
      const allSkillsRes = await fetch("/skills/my", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      const allSkills = await allSkillsRes.json();
      skill = allSkills.find(s => s.name.toLowerCase() === skillName.toLowerCase());
      if (!skill) throw new Error("Skill exists but not found in your skills");
    } else {
      throw new Error("Failed to create skill");
    }

    // Add skill to user
    await fetch(`/skills/add/${skill.id}`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` }
    });

    document.getElementById("new-skill-input").value = "";
    loadMySkills(); // refresh
  } catch (err) {
    console.error(err);
    alert("Помилка при додаванні навички");
  }
});


  } catch (err) {
    console.error(err);
    localStorage.removeItem("access_token");
    window.location.href = "/auth?mode=login";
  }
});
