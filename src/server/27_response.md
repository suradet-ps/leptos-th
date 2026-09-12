# การตอบกลับและการเปลี่ยนเส้นทาง

เอกซ์แทรกเตอร์เป็นวิธีง่ายๆ ในการเข้าถึงข้อมูลคำขอภายในฟังก์ชันฝั่งเซิร์ฟเวอร์ Leptos ยังมีวิธีแก้ไขการตอบกลับ HTTP โดยใช้ชนิด `ResponseOptions` (ดูเอกสารสำหรับชนิดของ [Actix](https://docs.rs/leptos_actix/latest/leptos_actix/struct.ResponseOptions.html) หรือ [Axum](https://docs.rs/leptos_axum/latest/leptos_axum/struct.ResponseOptions.html)) และฟังก์ชันช่วย `redirect` (ดูเอกสารสำหรับ [Actix](https://docs.rs/leptos_actix/latest/leptos_actix/fn.redirect.html) หรือ [Axum](https://docs.rs/leptos_axum/latest/leptos_axum/fn.redirect.html))

## `ResponseOptions`

`ResponseOptions` ถูกให้ผ่านคอนเท็กซ์ระหว่างการตอบกลับการเรนเดอร์ฝั่งเซิร์ฟเวอร์ครั้งแรก และระหว่างการเรียกฟังก์ชันฝั่งเซิร์ฟเวอร์ครั้งต่อๆ ไป มันช่วยให้คุณตั้งรหัสสถานะสำหรับการตอบกลับ HTTP หรือเพิ่มเฮดเดอร์ในการตอบกลับ HTTP ได้อย่างง่ายดาย เช่น เพื่อตั้งคุกกี้

```rust
#[server]
pub async fn tea_and_cookies() -> Result<(), ServerFnError> {
    use actix_web::{
        cookie::Cookie,
        http::header::HeaderValue,
        http::{header, StatusCode},
    };
    use leptos_actix::ResponseOptions;

    // pull ResponseOptions from context
    let response = expect_context::<ResponseOptions>();

    // set the HTTP status code
    response.set_status(StatusCode::IM_A_TEAPOT);

    // set a cookie in the HTTP response
    let cookie = Cookie::build("biscuits", "yes").finish();
    if let Ok(cookie) = HeaderValue::from_str(&cookie.to_string()) {
        response.insert_header(header::SET_COOKIE, cookie);
    }
    Ok(())
}
```

## `redirect`

การแก้ไขการตอบกลับ HTTP ที่พบบ่อยอย่างหนึ่งคือการเปลี่ยนเส้นทางไปยังหน้าอื่น การผสานรวม Actix และ Axum มีฟังก์ชัน `redirect` เพื่อให้เรื่องนี้ง่าย

```rust
#[server]
pub async fn login(
    username: String,
    password: String,
    remember: Option<String>,
) -> Result<(), ServerFnError> {
    const INVALID_CREDENTIALS: fn() -> ServerFnError = || -> ServerFnError {
        ServerFnError::ServerError("Invalid credentials".into())
    };

    // pull the DB pool and auth provider from context
    let pool = pool()?;
    let auth = auth()?;

    // check whether the user exists
    let user: User = User::get_from_username(username, &pool)
        .await
        .ok_or_else(INVALID_CREDENTIALS)?;

    // check whether the user has provided the correct password
    match verify(password, &user.password)? {
        // if the password is correct...
        true => {
            // log the user in
            auth.login_user(user.id);
            auth.remember_user(remember.is_some());

            // and redirect to the home page
            leptos_axum::redirect("/");
            Ok(())
        }
        // if not, return an error
        false => Err(INVALID_CREDENTIALS()),
    }
}
```

ฟังก์ชันฝั่งเซิร์ฟเวอร์นี้สามารถใช้ได้จากแอปพลิเคชันของคุณ `redirect` นี้ทำงานร่วมกับคอมโพเนนต์ `<ActionForm/>` ที่เสริมความสามารถแบบก้าวหน้าได้ดี: หากไม่มี JS/WASM การตอบกลับจากเซิร์ฟเวอร์จะเปลี่ยนเส้นทางเนื่องจากรหัสสถานะและเฮดเดอร์ หากมี JS/WASM `<ActionForm/>` จะตรวจจับการเปลี่ยนเส้นทางในการตอบกลับของฟังก์ชันฝั่งเซิร์ฟเวอร์ และใช้การนำทางฝั่งไคลเอนต์เพื่อเปลี่ยนเส้นทางไปยังหน้าใหม่
