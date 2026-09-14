# การตอบกลับและการเปลี่ยนเส้นทาง

เอกซ์แทรกเตอร์เป็นวิธีที่สะดวกและง่ายดายในการเข้าถึงข้อมูลคำขอ (request data) ภายในฟังก์ชันฝั่งเซิร์ฟเวอร์ นอกจากนี้ Leptos ยังเตรียมกลไกสำหรับปรับแต่งคำตอบ HTTP (HTTP response) ผ่านชนิดข้อมูล `ResponseOptions` (ดูเอกสารสำหรับ [Actix](https://docs.rs/leptos_actix/latest/leptos_actix/struct.ResponseOptions.html) หรือ [Axum](https://docs.rs/leptos_axum/latest/leptos_axum/struct.ResponseOptions.html)) และฟังก์ชันตัวช่วย `redirect` (ดูเอกสารสำหรับ [Actix](https://docs.rs/leptos_actix/latest/leptos_actix/fn.redirect.html) หรือ [Axum](https://docs.rs/leptos_axum/latest/leptos_axum/fn.redirect.html)) ไว้อีกด้วย

## `ResponseOptions`

`ResponseOptions` จะถูกส่งมอบผ่านระบบคอนเทกซ์ (context) ในระหว่างขั้นตอนการเรนเดอร์ตอบกลับบนเซิร์ฟเวอร์ในรอบแรก และในระหว่างการเรียกใช้งานฟังก์ชันฝั่งเซิร์ฟเวอร์ในรอบต่อ ๆ ไป มันช่วยให้คุณสามารถกำหนดรหัสสถานะ (status code) สำหรับคำตอบ HTTP หรือเพิ่มส่วนหัว (headers) เข้าไปในคำตอบ HTTP ได้อย่างง่ายดาย เช่น การตั้งค่าคุกกี้ (cookies)

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

การปรับแต่งคำตอบ HTTP ที่พบได้บ่อยอย่างหนึ่งคือการเปลี่ยนเส้นทาง (redirect) ไปยังหน้าอื่น ซึ่งการผสานรวมของทั้ง Actix และ Axum ต่างก็มีฟังก์ชัน `redirect` มาให้เพื่อให้คุณทำสิ่งนี้ได้อย่างสะดวกสบาย:

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

จากนั้นคุณสามารถเรียกใช้ฟังก์ชันฝั่งเซิร์ฟเวอร์นี้ได้จากทุกที่ในแอปพลิเคชันของคุณ โดยที่ `redirect` นี้จะทำงานร่วมกับคอมโพเนนต์ `<ActionForm/>` ที่รองรับการเสริมประสิทธิภาพอย่างต่อเนื่อง (progressive enhancement) ได้อย่างสมบูรณ์แบบ: หากเบราว์เซอร์ไม่มีหรือปิดการใช้งาน JS/WASM คำตอบจากเซิร์ฟเวอร์จะสั่ง redirect ทันทีผ่าน HTTP status code และ header ส่วนในกรณีที่มี JS/WASM ตัวคอมโพเนนต์ `<ActionForm/>` จะตรวจจับคำสั่ง redirect ในผลลัพธ์ของฟังก์ชันฝั่งเซิร์ฟเวอร์ แล้วเปลี่ยนเส้นทางไปยังหน้าใหม่โดยใช้ระบบการนำทางบนฝั่งไคลเอนต์ (client-side navigation) ให้โดยอัตโนมัติ
