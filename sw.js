
self.addEventListener("push", function (event) {

    let data = {
        title: "Examination Duty Reminder",
        message: "You have an upcoming examination duty."
    };

    if (event.data) {
        try {
            data = event.data.json();
        } catch (error) {
            data.message = event.data.text();
        }
    }

    const options = {
        body: data.message,
        icon: "/favicon.ico",
        badge: "/favicon.ico",
        tag: "exam-duty-reminder",
        renotify: true,
        data: {
            url: "/dashboard"
        }
    };

    event.waitUntil(
        self.registration.showNotification(
            data.title,
            options
        )
    );

});


self.addEventListener("notificationclick", function (event) {

    event.notification.close();

    event.waitUntil(
        clients.matchAll({
            type: "window",
            includeUncontrolled: true
        }).then(function (clientList) {

            for (const client of clientList) {

                if ("focus" in client) {
                    return client.focus();
                }

            }

            return clients.openWindow(
                event.notification.data.url
            );

        })
    );

});
