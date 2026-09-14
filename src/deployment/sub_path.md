# การดีพลอยบนพาธที่ไม่ใช่รูท (Non-Root Paths)

จนถึงตอนนี้ ขั้นตอนการดีพลอยทั้งหมดที่เราพูดถึงตั้งอยู่บนสมมติฐานว่าแอปพลิเคชันของคุณถูกดีพลอยไว้ที่พาธรูทของโดเมน (`/`) อย่างไรก็ตาม คุณยังสามารถดีพลอยแอปพลิเคชันของคุณไว้ที่พาธอื่นที่ไม่ใช่รูทได้เช่นกัน เช่น `/my-app`

หากคุณดีพลอยไว้ที่พาธที่ไม่ใช่รูท คุณจะต้องดำเนินการเพิ่มเติมอีกสองสามขั้นตอน เพื่อบอกให้แต่ละส่วนของแอปพลิเคชันรับรู้ว่าพาธฐาน (base path) ใหม่คืออะไร

## อัปเดต `base` ของเราเตอร์

คอมโพเนนต์ [`<Router/>`](https://docs.rs/leptos_router/latest/leptos_router/components/fn.Router.html) มี prop `base` สำหรับระบุพาธฐานของการจัดเส้นทาง ตัวอย่างเช่น หากคุณกำลังดีพลอยแอปพลิเคชันที่มีสามหน้าคือ `/`, `/about` และ `/contact` แล้วต้องการให้ทั้งหมดถูกเสิร์ฟภายใต้พาธ `/my-app` (ทำให้ทั้งสามเส้นทางกลายเป็น `/my-app`, `/my-app/about` และ `/my-app/contact`) คุณก็เพียงแค่กำหนด prop `base` ให้เป็น `"/my-app"`:

```rust
<Router base="/my-app">
    <Routes fallback=|| "Not found.">
        <Route path=path!("/") view=Home/>
        <Route path=path!("/about") view=About/>
        <Route path=path!("/contact") view=Contact/>
    </Routes>
</Router>
```

หากคุณใช้งานรีเวิร์สพร็อกซี (reverse proxy) มีแนวโน้มสูงที่เซิร์ฟเวอร์ของคุณจะ*เข้าใจว่า*ตัวเองกำลังให้บริการอยู่ที่ `/` ทั้งที่จริง ๆ แล้วพร็อกซีกำลังส่งต่อไปยัง `/my-app` แต่ในฝั่งเบราว์เซอร์ เราเตอร์จะยังคงมองเห็น URL เป็น `/my-app` อยู่ ในสถานการณ์นี้ คุณควรกำหนด prop `base` ตามเงื่อนไขโดยใช้ conditional compilation:
```rust
let base = if cfg!(feature = "hydrate") {
    "/my-app"
} else {
    "/"
};
// ...
<Router base> // ...
```

## อัปเดต `<HydrationScripts root/>`

หากคุณใช้การเรนเดอร์ฝั่งเซิร์ฟเวอร์ (SSR) คอมโพเนนต์ [`<HydrationScripts/>`](https://docs.rs/leptos/latest/leptos/hydration/fn.HydrationScripts.html) จะมีหน้าที่โหลดไฟล์ JS/WASM สำหรับทำ hydration ให้กับแอป คอมโพเนนต์นี้มี prop `root` ของตัวเองสำหรับระบุพาธฐานของสคริปต์ hydration ซึ่งหากสคริปต์เหล่านี้ถูกเสิร์ฟจากไดเรกทอรีย่อยด้วย คุณก็ควรกำหนดพาธฐานดังกล่าวลงใน prop `root` ด้วยเช่นกัน

## อัปเดต URL ของ Server Function

หากคุณใช้งาน server function ค่าเริ่มต้นของฟังก์ชันจะส่งคำขอไปยัง `/` หาก endpoint หรือตัวจัดการ server function ของคุณถูกเมานต์ไว้ที่พาธอื่น คุณสามารถกำหนดค่าใหม่ได้ผ่าน [`set_server_url`](https://docs.rs/leptos/latest/leptos/server_fn/client/fn.set_server_url.html)

## การตั้งค่า Trunk

หากคุณใช้การเรนเดอร์ฝั่งไคลเอนต์ (CSR) ร่วมกับ Trunk สามารถ[ดูเอกสารของ Trunk](https://trunk-rs.github.io/trunk/guide/assets/index.html#directives) เกี่ยวกับวิธีการกำหนดค่า public URL ผ่านอาร์กิวเมนต์ `--public-url`
