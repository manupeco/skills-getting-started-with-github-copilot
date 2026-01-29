document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      for (const [name, details] of Object.entries(activities)) {
        const card = document.createElement("div");
        card.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        card.innerHTML = `
          <h4>${name}</h4>
          <p><strong>Description:</strong> ${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Spots Available:</strong> ${spotsLeft} / ${details.max_participants}</p>
          <div class="participants-section">
            <strong>Current Participants:</strong>
            ${details.participants.length > 0
              ? `<ul class="participants-list">
                  ${details.participants.map(email => `
                    <li>
                      <span class="participant-email">${email}</span>
                      <button class="delete-btn" data-activity="${name}" data-email="${email}" title="Unregister participant" aria-label="Unregister participant">×</button>
                    </li>
                  `).join('')}
                </ul>`
              : '<p class="no-participants">No participants yet</p>'
            }
          </div>
        `;

        activitiesList.appendChild(card);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      }
    } catch (error) {
      console.error("Error loading activities:", error);
      activitiesList.innerHTML = "<p class=\"error\">Failed to load activities. Please try again later.</p>";
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;
    const messageDiv = document.getElementById("message");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (response.ok) {
        messageDiv.className = "message success";
        messageDiv.textContent = data.message;
        messageDiv.classList.remove("hidden");

        // Reset form and reload activities
        signupForm.reset();
        fetchActivities();
      } else {
        throw new Error(data.detail || "Signup failed");
      }
    } catch (error) {
      messageDiv.className = "message error";
      messageDiv.textContent = error.message;
      messageDiv.classList.remove("hidden");
    }

    // Hide message after 5 seconds
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  });

  // Handle delete button clicks
  activitiesList.addEventListener("click", async (event) => {
    if (event.target.classList.contains("delete-btn")) {
      const button = event.target;
      const activity = button.dataset.activity;
      const email = button.dataset.email;

      if (confirm(`Are you sure you want to unregister ${email} from ${activity}?`)) {
        try {
          const response = await fetch(
            `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
            {
              method: "DELETE",
            }
          );

          const data = await response.json();

          if (response.ok) {
            messageDiv.className = "message success";
            messageDiv.textContent = data.message;
            messageDiv.classList.remove("hidden");

            // Reload activities
            fetchActivities();
          } else {
            throw new Error(data.detail || "Unregister failed");
          }
        } catch (error) {
          messageDiv.className = "message error";
          messageDiv.textContent = error.message;
          messageDiv.classList.remove("hidden");
        }

        // Hide message after 5 seconds
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      }
    }
  });

  // Load activities on page load
  fetchActivities();
});
